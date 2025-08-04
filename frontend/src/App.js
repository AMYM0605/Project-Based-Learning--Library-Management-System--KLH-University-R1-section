import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (name, email, password, role = 'member') => {
    try {
      const response = await axios.post(`${API}/auth/register`, { name, email, password, role });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

// Login Component
const Login = ({ onToggle }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(email, password);
    if (!result.success) {
      setError(result.error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to Library System
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Email address"
            />
          </div>
          <div>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Password"
            />
          </div>
          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Sign in
            </button>
          </div>
          <div className="text-center">
            <button
              type="button"
              onClick={onToggle}
              className="text-indigo-600 hover:text-indigo-500"
            >
              Don't have an account? Register
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Register Component
const Register = ({ onToggle }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('member');
  const [error, setError] = useState('');
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await register(name, email, password, role);
    if (!result.success) {
      setError(result.error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Full name"
            />
          </div>
          <div>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Email address"
            />
          </div>
          <div>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Password"
            />
          </div>
          <div>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="member">Member</option>
              <option value="librarian">Librarian</option>
            </select>
          </div>
          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Sign up
            </button>
          </div>
          <div className="text-center">
            <button
              type="button"
              onClick={onToggle}
              className="text-indigo-600 hover:text-indigo-500"
            >
              Already have an account? Sign in
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Navigation Component
const Navigation = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('books');

  return (
    <nav className="bg-indigo-600 shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-white text-xl font-bold">Library Management System</h1>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setActiveTab('books')}
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                activeTab === 'books' ? 'bg-indigo-700 text-white' : 'text-indigo-100 hover:text-white'
              }`}
            >
              Books
            </button>
            {user?.role === 'librarian' && (
              <>
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'dashboard' ? 'bg-indigo-700 text-white' : 'text-indigo-100 hover:text-white'
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setActiveTab('analytics')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeTab === 'analytics' ? 'bg-indigo-700 text-white' : 'text-indigo-100 hover:text-white'
                  }`}
                >
                  Analytics
                </button>
              </>
            )}
            <button
              onClick={() => setActiveTab('borrows')}
              className={`px-3 py-2 rounded-md text-sm font-medium ${
                activeTab === 'borrows' ? 'bg-indigo-700 text-white' : 'text-indigo-100 hover:text-white'
              }`}
            >
              My Books
            </button>
            <span className="text-indigo-100">Welcome, {user?.name}</span>
            <button
              onClick={logout}
              className="bg-indigo-700 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-800"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
      <TabContent activeTab={activeTab} />
    </nav>
  );
};

// Books Component
const Books = () => {
  const [books, setBooks] = useState([]);
  const [search, setSearch] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const { user } = useAuth();

  const [newBook, setNewBook] = useState({
    title: '',
    author: '',
    isbn: '',
    genre: '',
    publication_year: '',
    description: '',
    total_copies: '',
    tags: ''
  });

  useEffect(() => {
    fetchBooks();
    if (user) {
      fetchRecommendations();
    }
  }, [search, user]);

  const fetchBooks = async () => {
    try {
      const response = await axios.get(`${API}/books?search=${search}`);
      setBooks(response.data);
    } catch (error) {
      console.error('Failed to fetch books:', error);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get(`${API}/recommendations/${user.id}`);
      setRecommendations(response.data);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    }
  };

  const handleAddBook = async (e) => {
    e.preventDefault();
    try {
      const bookData = {
        ...newBook,
        publication_year: parseInt(newBook.publication_year),
        total_copies: parseInt(newBook.total_copies),
        tags: newBook.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };
      
      await axios.post(`${API}/books`, bookData);
      setNewBook({
        title: '',
        author: '',
        isbn: '',
        genre: '',
        publication_year: '',
        description: '',
        total_copies: '',
        tags: ''
      });
      setShowAddForm(false);
      fetchBooks();
    } catch (error) {
      console.error('Failed to add book:', error);
      alert('Failed to add book: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const handleBorrowBook = async (bookId) => {
    try {
      await axios.post(`${API}/borrow`, { book_id: bookId, borrow_days: 14 });
      alert('Book borrowed successfully!');
      fetchBooks();
    } catch (error) {
      console.error('Failed to borrow book:', error);
      alert('Failed to borrow book: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      {/* Hero Section */}
      <div className="relative bg-gray-900 rounded-lg overflow-hidden mb-8">
        <img 
          src="https://images.unsplash.com/photo-1554896541-dff010081afe?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1ODB8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBsaWJyYXJ5fGVufDB8fHx8MTc1NDI5NDQ3MXww&ixlib=rb-4.1.0&q=85"
          alt="Modern Library"
          className="w-full h-64 object-cover opacity-70"
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-4">Welcome to Our Library</h1>
            <p className="text-xl text-gray-200">Discover, Learn, and Grow</p>
          </div>
        </div>
      </div>

      {/* Search and Add Book */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
          <div className="flex-1 max-w-xs">
            <input
              type="text"
              placeholder="Search books..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          {user?.role === 'librarian' && (
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
            >
              Add New Book
            </button>
          )}
        </div>

        {/* Add Book Form */}
        {showAddForm && (
          <form onSubmit={handleAddBook} className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
            <input
              type="text"
              placeholder="Title"
              value={newBook.title}
              onChange={(e) => setNewBook({...newBook, title: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
            <input
              type="text"
              placeholder="Author"
              value={newBook.author}
              onChange={(e) => setNewBook({...newBook, author: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
            <input
              type="text"
              placeholder="ISBN"
              value={newBook.isbn}
              onChange={(e) => setNewBook({...newBook, isbn: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
            <input
              type="text"
              placeholder="Genre"
              value={newBook.genre}
              onChange={(e) => setNewBook({...newBook, genre: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
            <input
              type="number"
              placeholder="Publication Year"
              value={newBook.publication_year}
              onChange={(e) => setNewBook({...newBook, publication_year: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
            <input
              type="number"
              placeholder="Total Copies"
              value={newBook.total_copies}
              onChange={(e) => setNewBook({...newBook, total_copies: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
            <input
              type="text"
              placeholder="Tags (comma separated)"
              value={newBook.tags}
              onChange={(e) => setNewBook({...newBook, tags: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
            <textarea
              placeholder="Description"
              value={newBook.description}
              onChange={(e) => setNewBook({...newBook, description: e.target.value})}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:col-span-2"
              rows="3"
              required
            />
            <div className="sm:col-span-2">
              <button
                type="submit"
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 mr-2"
              >
                Add Book
              </button>
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recommended for You</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {recommendations.slice(0, 3).map((rec) => (
              <div key={rec.book_id} className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900">{rec.title}</h3>
                <p className="text-sm text-gray-600">by {rec.author}</p>
                <p className="text-xs text-gray-500 mt-2">{rec.reason}</p>
                <div className="mt-2">
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {Math.round(rec.similarity_score * 100)}% match
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Books Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {books.map((book) => (
          <div key={book.id} className="bg-white shadow rounded-lg overflow-hidden">
            <div className="p-6">
              <h3 className="text-lg font-medium text-gray-900">{book.title}</h3>
              <p className="text-sm text-gray-600">by {book.author}</p>
              <p className="text-sm text-gray-500 mt-2">Genre: {book.genre}</p>
              <p className="text-sm text-gray-500">Published: {book.publication_year}</p>
              <p className="text-sm text-gray-500">Available: {book.available_copies}/{book.total_copies}</p>
              <p className="text-sm text-gray-700 mt-2">{book.description}</p>
              
              {book.tags.length > 0 && (
                <div className="mt-2">
                  {book.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="inline-block bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded mr-2 mb-2"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              
              <div className="mt-4">
                {book.available_copies > 0 ? (
                  <button
                    onClick={() => handleBorrowBook(book.id)}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 text-sm"
                  >
                    Borrow Book
                  </button>
                ) : (
                  <span className="bg-red-100 text-red-800 px-4 py-2 rounded-md text-sm">
                    Not Available
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// My Books Component
const MyBooks = () => {
  const [borrows, setBorrows] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    fetchBorrows();
  }, []);

  const fetchBorrows = async () => {
    try {
      const response = await axios.get(`${API}/borrows`);
      setBorrows(response.data);
    } catch (error) {
      console.error('Failed to fetch borrows:', error);
    }
  };

  const handleReturnBook = async (borrowId) => {
    try {
      const response = await axios.post(`${API}/return`, { borrow_id: borrowId });
      alert(`Book returned successfully! Fine: $${response.data.fine_amount}`);
      fetchBorrows();
    } catch (error) {
      console.error('Failed to return book:', error);
      alert('Failed to return book: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'borrowed': return 'bg-blue-100 text-blue-800';
      case 'overdue': return 'bg-red-100 text-red-800';
      case 'returned': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">My Borrowed Books</h2>
          
          {borrows.length === 0 ? (
            <p className="text-gray-500">No books borrowed yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Book
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Author
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Borrowed Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Due Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {borrows.map((borrow) => (
                    <tr key={borrow.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {borrow.book_title}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {borrow.book_author}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(borrow.borrowed_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(borrow.due_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(borrow.status)}`}>
                          {borrow.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {borrow.status === 'borrowed' || borrow.status === 'overdue' ? (
                          <button
                            onClick={() => handleReturnBook(borrow.id)}
                            className="text-indigo-600 hover:text-indigo-900"
                          >
                            Return Book
                          </button>
                        ) : borrow.fine_amount > 0 ? (
                          <span className="text-red-600">Fine: ${borrow.fine_amount}</span>
                        ) : (
                          <span className="text-green-600">Completed</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Dashboard Component (Librarian Only)
const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [overdueBooks, setOverdueBooks] = useState([]);

  useEffect(() => {
    fetchDashboardStats();
    fetchOverdueBooks();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    }
  };

  const fetchOverdueBooks = async () => {
    try {
      const response = await axios.get(`${API}/overdue`);
      setOverdueBooks(response.data);
    } catch (error) {
      console.error('Failed to fetch overdue books:', error);
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-indigo-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">B</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Books</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.total_books || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">U</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.total_users || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">A</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Active Borrows</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.active_borrows || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">O</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Overdue Books</dt>
                  <dd className="text-lg font-medium text-gray-900">{stats.overdue_books || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Overdue Books */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Overdue Books</h2>
          
          {overdueBooks.length === 0 ? (
            <p className="text-gray-500">No overdue books.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Book
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Due Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Days Overdue
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fine
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {overdueBooks.map((borrow) => (
                    <tr key={borrow.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {borrow.book_title}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {borrow.user_name} ({borrow.user_email})
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(borrow.due_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                        {borrow.overdue_days} days
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                        ${borrow.calculated_fine}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Analytics Component (Librarian Only)
const Analytics = () => {
  const [demandForecast, setDemandForecast] = useState([]);
  const [overduePredictions, setOverduePredictions] = useState([]);

  useEffect(() => {
    fetchDemandForecast();
    fetchOverduePredictions();
  }, []);

  const fetchDemandForecast = async () => {
    try {
      const response = await axios.get(`${API}/analytics/demand-forecast`);
      setDemandForecast(response.data);
    } catch (error) {
      console.error('Failed to fetch demand forecast:', error);
    }
  };

  const fetchOverduePredictions = async () => {
    try {
      const response = await axios.get(`${API}/analytics/overdue-predictions`);
      setOverduePredictions(response.data);
    } catch (error) {
      console.error('Failed to fetch overdue predictions:', error);
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'High': return 'bg-red-100 text-red-800';
      case 'Medium': return 'bg-yellow-100 text-yellow-800';
      case 'Low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Demand Forecast */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Demand Forecast</h2>
            
            {demandForecast.length === 0 ? (
              <p className="text-gray-500">No forecast data available.</p>
            ) : (
              <div className="space-y-4">
                {demandForecast.slice(0, 10).map((forecast) => (
                  <div key={forecast.book_id} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900">{forecast.title}</h3>
                    <div className="mt-2 flex justify-between items-center">
                      <span className="text-sm text-gray-600">
                        Predicted Demand: {forecast.predicted_demand}
                      </span>
                      <span className="text-sm text-gray-600">
                        Confidence: {Math.round(forecast.confidence * 100)}%
                      </span>
                    </div>
                    <div className="mt-2 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${forecast.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Overdue Predictions */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Overdue Risk Predictions</h2>
            
            {overduePredictions.length === 0 ? (
              <p className="text-gray-500">No prediction data available.</p>
            ) : (
              <div className="space-y-4">
                {overduePredictions.slice(0, 10).map((prediction) => (
                  <div key={prediction.borrow_id} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900">{prediction.book_title}</h3>
                    <div className="mt-2 flex justify-between items-center">
                      <span className="text-sm text-gray-600">
                        Risk: {Math.round(prediction.probability * 100)}%
                      </span>
                      <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${getRiskColor(prediction.risk_level)}`}>
                        {prediction.risk_level} Risk
                      </span>
                    </div>
                    <div className="mt-2 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          prediction.risk_level === 'High' ? 'bg-red-600' :
                          prediction.risk_level === 'Medium' ? 'bg-yellow-600' : 'bg-green-600'
                        }`}
                        style={{ width: `${prediction.probability * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Tab Content Component
const TabContent = ({ activeTab }) => {
  const { user } = useAuth();

  switch (activeTab) {
    case 'books':
      return <Books />;
    case 'borrows':
      return <MyBooks />;
    case 'dashboard':
      return user?.role === 'librarian' ? <Dashboard /> : <Books />;
    case 'analytics':
      return user?.role === 'librarian' ? <Analytics /> : <Books />;
    default:
      return <Books />;
  }
};

// Main App Component
const App = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <AuthenticatedApp isLogin={isLogin} setIsLogin={setIsLogin} />
      </div>
    </AuthProvider>
  );
};

const AuthenticatedApp = ({ isLogin, setIsLogin }) => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return isLogin ? (
      <Login onToggle={() => setIsLogin(false)} />
    ) : (
      <Register onToggle={() => setIsLogin(true)} />
    );
  }

  return <Navigation />;
};

export default App;