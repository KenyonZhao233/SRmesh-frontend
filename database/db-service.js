const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');

const app = express();
const port = 3001;

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

// Database configuration
const dbConfig = {
    host: 'localhost',
    user: 'root',
    password: 'cnptzhaoky', // Change this to your MySQL password
    database: 'network_delay_db'
};

// Create connection pool
const pool = mysql.createPool(dbConfig);

// API route to get delay data for a specific date
app.get('/api/delay-data/:date', (req, res) => {
    const date = req.params.date;
    
    // Validate date format (YYYY-MM-DD)
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(date)) {
        return res.status(400).json({ error: 'Invalid date format. Use YYYY-MM-DD' });
    }
    
    const query = `
        SELECT slice, src, dst, timestamp, delay 
        FROM delay_data 
        WHERE DATE(timestamp) = ? 
        ORDER BY timestamp, slice
    `;
    
    pool.execute(query, [date], (err, results) => {
        if (err) {
            console.error('Database query error:', err);
            return res.status(500).json({ error: 'Database query failed' });
        }
        
        res.json({
            date: date,
            total_records: results.length,
            data: results
        });
    });
});

// API route to get summary statistics for a specific date
app.get('/api/delay-summary/:date', (req, res) => {
    const date = req.params.date;
    
    const query = `
        SELECT 
            slice,
            COUNT(*) as record_count,
            ROUND(AVG(delay), 3) as avg_delay,
            ROUND(MIN(delay), 3) as min_delay,
            ROUND(MAX(delay), 3) as max_delay
        FROM delay_data 
        WHERE DATE(timestamp) = ? 
        GROUP BY slice
        ORDER BY slice
    `;
    
    pool.execute(query, [date], (err, results) => {
        if (err) {
            console.error('Database query error:', err);
            return res.status(500).json({ error: 'Database query failed' });
        }
        
        res.json({
            date: date,
            summary: results
        });
    });
});

// API route to get hourly statistics for a specific date
app.get('/api/delay-hourly/:date', (req, res) => {
    const date = req.params.date;
    
    const query = `
        SELECT 
            slice,
            HOUR(timestamp) as hour,
            ROUND(AVG(delay), 3) as avg_delay,
            COUNT(*) as record_count
        FROM delay_data 
        WHERE DATE(timestamp) = ? 
        GROUP BY slice, HOUR(timestamp)
        ORDER BY slice, hour
    `;
    
    pool.execute(query, [date], (err, results) => {
        if (err) {
            console.error('Database query error:', err);
            return res.status(500).json({ error: 'Database query failed' });
        }
        
        res.json({
            date: date,
            hourly_data: results
        });
    });
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    pool.execute('SELECT 1', (err, results) => {
        if (err) {
            return res.status(500).json({ status: 'error', message: 'Database connection failed' });
        }
        res.json({ status: 'ok', message: 'Service is running' });
    });
});

app.listen(port, () => {
    console.log(`API server running at http://localhost:${port}`);
    console.log(`Health check: http://localhost:${port}/api/health`);
    console.log(`Example API: http://localhost:${port}/api/delay-data/2025-01-01`);
});

module.exports = app;
