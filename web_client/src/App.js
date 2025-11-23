import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';
import { Chart as ChartJS } from 'chart.js/auto';

function App() {
  // Auth State
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [error, setError] = useState('');

  // Data State
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);

  // --- HELPER: Get Auth Headers ---
  const getAuthHeader = useCallback(() => {
    return { auth: { username, password } };
  }, [username, password]);

  // --- ACTION: Fetch History ---
  const fetchHistory = useCallback(async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/history/', getAuthHeader());
      setHistory(res.data);
    } catch (err) { 
      console.error(err); 
      if(err.response?.status === 401) setIsLoggedIn(false);
    }
  }, [getAuthHeader]);

  // --- EFFECT: Load Data on Login ---
  useEffect(() => {
    if (isLoggedIn) {
      fetchHistory();
    }
  }, [isLoggedIn, fetchHistory]);

  // --- AUTH ACTIONS ---
  const handleAuth = async () => {
    setError('');
    if (!username || !password) {
      setError('Please fill in all fields');
      return;
    }

    if (isLoginMode) {
      // LOGIN
      try {
        await axios.get('http://127.0.0.1:8000/api/history/', getAuthHeader());
        setIsLoggedIn(true);
      } catch (err) {
        setError('Invalid Credentials');
      }
    } else {
      // SIGNUP
      try {
        await axios.post('http://127.0.0.1:8000/api/register/', { username, password });
        alert("Account created! Please log in.");
        setIsLoginMode(true);
      } catch (err) {
        setError('Username already exists or invalid data.');
      }
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUsername('');
    setPassword('');
    setData(null);
    setHistory([]);
  };

  // --- DATA ACTIONS ---
  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        ...getAuthHeader()
      });
      setData(res.data);
      fetchHistory();
    } catch (err) { alert("Upload Failed"); }
  };

  const downloadPDF = (id) => {
    axios.get(`http://127.0.0.1:8000/api/pdf/${id}/`, { responseType: 'blob', ...getAuthHeader() })
      .then(res => {
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `report_${id}.pdf`);
        document.body.appendChild(link);
        link.click();
      });
  };

  // --- RENDER AUTH SCREEN ---
  if (!isLoggedIn) {
    return (
      <div className="auth-wrapper">
        <div className="auth-card">
          <h2>{isLoginMode ? 'Welcome Back' : 'Create Account'}</h2>
          {error && <div className="alert alert-danger btn-sm">{error}</div>}
          
          <input 
            className="form-control custom-input" 
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input 
            className="form-control custom-input" 
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          
          <button className="btn-gradient" onClick={handleAuth}>
            {isLoginMode ? 'Sign In' : 'Sign Up'}
          </button>

          <div className="toggle-text">
            {isLoginMode ? "New here?" : "Already have an account?"}
            <span className="toggle-link" onClick={() => {
              setIsLoginMode(!isLoginMode);
              setError('');
            }}>
              {isLoginMode ? "Create Account" : "Login"}
            </span>
          </div>
        </div>
      </div>
    );
  }

  // --- RENDER DASHBOARD ---
  return (
    <div style={{ background: '#f4f6f9', minHeight: '100vh', padding: '20px' }}>
      <div className="container">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h3 style={{color: '#2d3748'}}>Chemical Visualizer</h3>
          <button onClick={handleLogout} className="btn btn-outline-danger">Logout</button>
        </div>

        {/* Upload Card */}
        <div className="card border-0 shadow-sm p-4 mb-4" style={{borderRadius: '12px'}}>
          <div className="row align-items-center">
            <div className="col-md-8">
              <input type="file" className="form-control" onChange={(e) => setFile(e.target.files[0])} />
            </div>
            <div className="col-md-4">
              <button onClick={handleUpload} className="btn btn-primary w-100" style={{background: '#667eea', border: 'none'}}>
                Upload & Analyze
              </button>
            </div>
          </div>
        </div>

        <div className="row">
          {/* Left: Charts & Data */}
          <div className="col-md-8">
            {data && (
              <>
                {/* Stats */}
                <div className="row mb-4">
                  {Object.entries(data.stats).map(([key, val]) => (
                    <div className="col-md-3" key={key}>
                      <div className="card border-0 shadow-sm p-3 text-center" style={{borderRadius: '12px'}}>
                        <small className="text-muted text-uppercase" style={{fontSize: '0.7rem'}}>{key.replace('avg_', '')}</small>
                        <h5 className="mb-0 text-primary">{typeof val === 'number' ? val.toFixed(2) : val}</h5>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Chart */}
                <div className="card border-0 shadow-sm p-4 mb-4" style={{borderRadius: '12px'}}>
                  <h5 className="mb-3">Distribution</h5>
                  <div style={{height: '300px'}}>
                    <Bar data={{
                      labels: Object.keys(data.distribution),
                      datasets: [{
                        label: 'Count',
                        data: Object.values(data.distribution),
                        backgroundColor: '#667eea',
                        borderRadius: 5
                      }]
                    }} options={{maintainAspectRatio:false}} />
                  </div>
                </div>
                
                <button onClick={() => downloadPDF(data.id)} className="btn btn-dark mb-4">Download Full Report PDF</button>
              </>
            )}
          </div>

          {/* Right: History Sidebar */}
          <div className="col-md-4">
            <div className="card border-0 shadow-sm p-3" style={{borderRadius: '12px'}}>
              <h5 className="mb-3" style={{color: '#4a5568', fontWeight: '700'}}>Recent Uploads</h5>
              
              {history.length === 0 ? (
                <p className="text-muted text-center mt-3">No history found.</p>
              ) : (
                <div className="list-group list-group-flush">
                  {history.map((h, index) => (
                    <div key={h.id} className="list-group-item border-0 mb-2 p-3 d-flex justify-content-between align-items-center" 
                         style={{
                           background: '#fff', 
                           borderRadius: '10px',
                           boxShadow: '0 2px 6px rgba(0,0,0,0.04)',
                           transition: 'transform 0.2s ease'
                         }}>
                      
                      <div className="d-flex align-items-center">
                        {/* Gradient Number Badge */}
                        <div style={{
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white',
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: 'bold',
                          marginRight: '12px',
                          fontSize: '0.9rem',
                          flexShrink: 0
                        }}>
                          {index + 1}
                        </div>
                        
                        <div style={{ overflow: 'hidden' }}>
                          {/* Filename with truncation */}
                          <div style={{
                            fontWeight: '600', 
                            color: '#2d3748',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            maxWidth: '120px' 
                          }} title={h.filename}>
                            {h.filename}
                          </div>
                          <small style={{color: '#a0aec0', fontSize: '0.8rem'}}>{h.date}</small>
                        </div>
                      </div>

                      <button 
                        onClick={() => downloadPDF(h.id)} 
                        className="btn btn-sm"
                        style={{
                          color: '#667eea', 
                          background: '#ebf4ff', 
                          border: 'none',
                          fontWeight: '600',
                          padding: '6px 12px',
                          borderRadius: '6px',
                          fontSize: '0.8rem'
                        }}
                      >
                        PDF
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
