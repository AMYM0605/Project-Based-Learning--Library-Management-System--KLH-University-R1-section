from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import hashlib
import jwt
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Library Management System", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"

# Authentication Models
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "member"  # member or librarian

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    role: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reading_history: List[str] = []
    current_borrowings: List[str] = []

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: datetime
    current_borrowings: List[str] = []

# Book Models
class Book(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    author: str
    isbn: str
    genre: str
    publication_year: int
    description: str
    total_copies: int
    available_copies: int
    tags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str
    genre: str
    publication_year: int
    description: str
    total_copies: int
    tags: List[str] = []

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    description: Optional[str] = None
    total_copies: Optional[int] = None
    tags: Optional[List[str]] = None

# Borrowing Models
class BorrowRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    book_id: str
    borrowed_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime
    returned_at: Optional[datetime] = None
    status: str = "borrowed"  # borrowed, returned, overdue
    fine_amount: float = 0.0

class BorrowRequest(BaseModel):
    book_id: str
    borrow_days: int = 14

class ReturnRequest(BaseModel):
    borrow_id: str

# AI/ML Models
class BookRecommendation(BaseModel):
    book_id: str
    title: str
    author: str
    similarity_score: float
    reason: str

class DemandForecast(BaseModel):
    book_id: str
    title: str
    predicted_demand: float
    confidence: float

class OverduePrediction(BaseModel):
    borrow_id: str
    user_id: str
    book_title: str
    probability: float
    risk_level: str

# Utility functions
def clean_mongo_doc(doc):
    """Remove MongoDB ObjectId fields that can't be JSON serialized"""
    if isinstance(doc, dict):
        return {k: v for k, v in doc.items() if k != '_id'}
    elif isinstance(doc, list):
        return [clean_mongo_doc(item) for item in doc]
    return doc

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

# Authentication endpoints
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role,
        password_hash=hash_password(user_data.password)
    )
    
    await db.users.insert_one(user.dict())
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user.dict())
    }

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

# Book Management endpoints
@api_router.post("/books", response_model=Book)
async def create_book(book_data: BookCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "librarian":
        raise HTTPException(status_code=403, detail="Only librarians can add books")
    
    book = Book(**book_data.dict(), available_copies=book_data.total_copies)
    await db.books.insert_one(book.dict())
    return book

@api_router.get("/books", response_model=List[Book])
async def get_books(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    genre: Optional[str] = None,
    author: Optional[str] = None
):
    query = {}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"author": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]
    if genre:
        query["genre"] = {"$regex": genre, "$options": "i"}
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    
    books = await db.books.find(query).skip(skip).limit(limit).to_list(limit)
    return [Book(**book) for book in books]

@api_router.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: str):
    book = await db.books.find_one({"id": book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return Book(**book)

@api_router.put("/books/{book_id}", response_model=Book)
async def update_book(
    book_id: str,
    book_data: BookUpdate,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "librarian":
        raise HTTPException(status_code=403, detail="Only librarians can update books")
    
    book = await db.books.find_one({"id": book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    update_data = {k: v for k, v in book_data.dict().items() if v is not None}
    
    if update_data:
        await db.books.update_one({"id": book_id}, {"$set": update_data})
        updated_book = await db.books.find_one({"id": book_id})
        return Book(**updated_book)
    
    return Book(**book)

@api_router.delete("/books/{book_id}")
async def delete_book(book_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "librarian":
        raise HTTPException(status_code=403, detail="Only librarians can delete books")
    
    result = await db.books.delete_one({"id": book_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return {"message": "Book deleted successfully"}

# Borrowing System endpoints
@api_router.post("/borrow", response_model=BorrowRecord)
async def borrow_book(
    borrow_data: BorrowRequest,
    current_user: User = Depends(get_current_user)
):
    # Check if book exists and available
    book = await db.books.find_one({"id": borrow_data.book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book["available_copies"] <= 0:
        raise HTTPException(status_code=400, detail="Book not available")
    
    # Check if user already borrowed this book
    existing_borrow = await db.borrows.find_one({
        "user_id": current_user.id,
        "book_id": borrow_data.book_id,
        "status": "borrowed"
    })
    if existing_borrow:
        raise HTTPException(status_code=400, detail="You already have this book borrowed")
    
    # Create borrow record
    due_date = datetime.utcnow() + timedelta(days=borrow_data.borrow_days)
    borrow_record = BorrowRecord(
        user_id=current_user.id,
        book_id=borrow_data.book_id,
        due_date=due_date
    )
    
    # Update book availability
    await db.books.update_one(
        {"id": borrow_data.book_id},
        {"$inc": {"available_copies": -1}}
    )
    
    # Update user's current borrowings
    await db.users.update_one(
        {"id": current_user.id},
        {"$push": {"current_borrowings": borrow_record.id}}
    )
    
    await db.borrows.insert_one(borrow_record.dict())
    return borrow_record

@api_router.post("/return")
async def return_book(
    return_data: ReturnRequest,
    current_user: User = Depends(get_current_user)
):
    borrow_record = await db.borrows.find_one({"id": return_data.borrow_id})
    if not borrow_record:
        raise HTTPException(status_code=404, detail="Borrow record not found")
    
    if borrow_record["user_id"] != current_user.id and current_user.role != "librarian":
        raise HTTPException(status_code=403, detail="Not authorized to return this book")
    
    if borrow_record["status"] == "returned":
        raise HTTPException(status_code=400, detail="Book already returned")
    
    # Calculate fine if overdue
    fine_amount = 0.0
    return_date = datetime.utcnow()
    if return_date > borrow_record["due_date"]:
        overdue_days = (return_date - borrow_record["due_date"]).days
        fine_amount = overdue_days * 1.0  # $1 per day
    
    # Update borrow record
    await db.borrows.update_one(
        {"id": return_data.borrow_id},
        {
            "$set": {
                "returned_at": return_date,
                "status": "returned",
                "fine_amount": fine_amount
            }
        }
    )
    
    # Update book availability
    await db.books.update_one(
        {"id": borrow_record["book_id"]},
        {"$inc": {"available_copies": 1}}
    )
    
    # Update user's borrowings and reading history
    await db.users.update_one(
        {"id": borrow_record["user_id"]},
        {
            "$pull": {"current_borrowings": return_data.borrow_id},
            "$push": {"reading_history": borrow_record["book_id"]}
        }
    )
    
    return {
        "message": "Book returned successfully",
        "fine_amount": fine_amount
    }

@api_router.get("/borrows", response_model=List[Dict[str, Any]])
async def get_borrows(current_user: User = Depends(get_current_user)):
    if current_user.role == "librarian":
        borrows = await db.borrows.find().to_list(1000)
    else:
        borrows = await db.borrows.find({"user_id": current_user.id}).to_list(1000)
    
    # Enrich with book and user details
    enriched_borrows = []
    for borrow in borrows:
        book = await db.books.find_one({"id": borrow["book_id"]})
        user = await db.users.find_one({"id": borrow["user_id"]})
        
        enriched_borrow = {
            **borrow,
            "book_title": book["title"] if book else "Unknown",
            "book_author": book["author"] if book else "Unknown",
            "user_name": user["name"] if user else "Unknown"
        }
        enriched_borrows.append(enriched_borrow)
    
    return enriched_borrows

@api_router.get("/overdue", response_model=List[Dict[str, Any]])
async def get_overdue_books(current_user: User = Depends(get_current_user)):
    if current_user.role != "librarian":
        raise HTTPException(status_code=403, detail="Only librarians can view overdue books")
    
    current_time = datetime.utcnow()
    overdue_borrows = await db.borrows.find({
        "status": "borrowed",
        "due_date": {"$lt": current_time}
    }).to_list(1000)
    
    # Update status to overdue
    for borrow in overdue_borrows:
        await db.borrows.update_one(
            {"id": borrow["id"]},
            {"$set": {"status": "overdue"}}
        )
    
    # Enrich with details
    enriched_overdue = []
    for borrow in overdue_borrows:
        book = await db.books.find_one({"id": borrow["book_id"]})
        user = await db.users.find_one({"id": borrow["user_id"]})
        
        overdue_days = (current_time - borrow["due_date"]).days
        fine_amount = overdue_days * 1.0
        
        enriched_borrow = {
            **borrow,
            "book_title": book["title"] if book else "Unknown",
            "book_author": book["author"] if book else "Unknown",
            "user_name": user["name"] if user else "Unknown",
            "user_email": user["email"] if user else "Unknown",
            "overdue_days": overdue_days,
            "calculated_fine": fine_amount
        }
        enriched_overdue.append(enriched_borrow)
    
    return enriched_overdue

# AI/ML endpoints
@api_router.get("/recommendations/{user_id}", response_model=List[BookRecommendation])
async def get_book_recommendations(user_id: str, limit: int = 5):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's reading history
    reading_history = user.get("reading_history", [])
    if not reading_history:
        # If no history, recommend popular books
        popular_books = await db.books.find().sort("created_at", -1).limit(limit).to_list(limit)
        recommendations = []
        for book in popular_books:
            rec = BookRecommendation(
                book_id=book["id"],
                title=book["title"],
                author=book["author"],
                similarity_score=0.5,
                reason="Popular book"
            )
            recommendations.append(rec)
        return recommendations
    
    # Get books user has read
    read_books = await db.books.find({"id": {"$in": reading_history}}).to_list(1000)
    all_books = await db.books.find().to_list(1000)
    
    # Simple content-based filtering using genres and tags
    user_genres = set()
    user_tags = set()
    
    for book in read_books:
        user_genres.add(book["genre"])
        user_tags.update(book.get("tags", []))
    
    recommendations = []
    for book in all_books:
        if book["id"] in reading_history:
            continue
        
        score = 0.0
        reasons = []
        
        # Genre similarity
        if book["genre"] in user_genres:
            score += 0.5
            reasons.append(f"Similar genre: {book['genre']}")
        
        # Tag similarity
        book_tags = set(book.get("tags", []))
        common_tags = user_tags.intersection(book_tags)
        if common_tags:
            score += len(common_tags) * 0.2
            reasons.append(f"Common tags: {', '.join(list(common_tags)[:2])}")
        
        if score > 0:
            rec = BookRecommendation(
                book_id=book["id"],
                title=book["title"],
                author=book["author"],
                similarity_score=score,
                reason="; ".join(reasons) if reasons else "Recommended for you"
            )
            recommendations.append(rec)
    
    # Sort by similarity score and return top recommendations
    recommendations.sort(key=lambda x: x.similarity_score, reverse=True)
    return recommendations[:limit]

@api_router.get("/analytics/demand-forecast", response_model=List[DemandForecast])
async def get_demand_forecast(current_user: User = Depends(get_current_user)):
    if current_user.role != "librarian":
        raise HTTPException(status_code=403, detail="Only librarians can view analytics")
    
    # Simple demand forecasting based on borrowing patterns
    books = await db.books.find().to_list(1000)
    forecasts = []
    
    for book in books:
        # Count recent borrows (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_borrows = await db.borrows.count_documents({
            "book_id": book["id"],
            "borrowed_at": {"$gte": thirty_days_ago}
        })
        
        # Simple prediction: recent borrows * 2 for next month
        predicted_demand = recent_borrows * 2
        confidence = min(0.9, 0.5 + (recent_borrows * 0.1))
        
        forecast = DemandForecast(
            book_id=book["id"],
            title=book["title"],
            predicted_demand=predicted_demand,
            confidence=confidence
        )
        forecasts.append(forecast)
    
    # Sort by predicted demand
    forecasts.sort(key=lambda x: x.predicted_demand, reverse=True)
    return forecasts[:20]

@api_router.get("/analytics/overdue-predictions", response_model=List[OverduePrediction])
async def get_overdue_predictions(current_user: User = Depends(get_current_user)):
    if current_user.role != "librarian":
        raise HTTPException(status_code=403, detail="Only librarians can view analytics")
    
    # Get current borrowed books
    current_borrows = await db.borrows.find({"status": "borrowed"}).to_list(1000)
    predictions = []
    
    for borrow in current_borrows:
        user = await db.users.find_one({"id": borrow["user_id"]})
        book = await db.books.find_one({"id": borrow["book_id"]})
        
        if not user or not book:
            continue
        
        # Simple prediction based on days until due and user history
        days_until_due = (borrow["due_date"] - datetime.utcnow()).days
        
        # Check user's past overdue rate
        user_total_borrows = await db.borrows.count_documents({"user_id": borrow["user_id"]})
        user_overdue_count = await db.borrows.count_documents({
            "user_id": borrow["user_id"],
            "status": {"$in": ["overdue", "returned"]},
            "returned_at": {"$gt": "$due_date"}
        })
        
        overdue_rate = user_overdue_count / max(user_total_borrows, 1)
        
        # Calculate probability
        if days_until_due <= 0:
            probability = 0.95
        elif days_until_due <= 2:
            probability = 0.7 + (overdue_rate * 0.2)
        elif days_until_due <= 5:
            probability = 0.4 + (overdue_rate * 0.3)
        else:
            probability = overdue_rate
        
        # Determine risk level
        if probability >= 0.7:
            risk_level = "High"
        elif probability >= 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        prediction = OverduePrediction(
            borrow_id=borrow["id"],
            user_id=borrow["user_id"],
            book_title=book["title"],
            probability=probability,
            risk_level=risk_level
        )
        predictions.append(prediction)
    
    # Sort by probability
    predictions.sort(key=lambda x: x.probability, reverse=True)
    return predictions

# Dashboard endpoints
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    if current_user.role != "librarian":
        raise HTTPException(status_code=403, detail="Only librarians can view dashboard")
    
    total_books = await db.books.count_documents({})
    total_users = await db.users.count_documents({"role": "member"})
    active_borrows = await db.borrows.count_documents({"status": "borrowed"})
    overdue_books = await db.borrows.count_documents({"status": "overdue"})
    
    # Recent activity
    recent_borrows = await db.borrows.find().sort("borrowed_at", -1).limit(5).to_list(5)
    
    return {
        "total_books": total_books,
        "total_users": total_users,
        "active_borrows": active_borrows,
        "overdue_books": overdue_books,
        "recent_activity": recent_borrows
    }

# User Management (for librarians)
@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: User = Depends(get_current_user)):
    if current_user.role != "librarian":
        raise HTTPException(status_code=403, detail="Only librarians can view users")
    
    users = await db.users.find({"role": "member"}).to_list(1000)
    return [UserResponse(**user) for user in users]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()