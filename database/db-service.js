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

// Device Groups API
app.get('/api/device-groups', (req, res) => {
    const query = `
        SELECT dg.id, dg.name, dg.device_type, dg.description, dg.created_at, COUNT(d.id) as device_count
        FROM device_groups dg
        LEFT JOIN devices d ON dg.id = d.group_id
        GROUP BY dg.id, dg.name, dg.device_type, dg.description, dg.created_at
        ORDER BY dg.created_at DESC
    `;
    
    pool.execute(query, (err, results) => {
        if (err) {
            console.error('Database query error:', err);
            return res.status(500).json({ error: 'Database query failed' });
        }
        res.json(results);
    });
});

app.post('/api/device-groups', (req, res) => {
    const { name, device_type, description } = req.body;
    
    if (!name || !device_type) {
        return res.status(400).json({ error: 'Name and device_type are required' });
    }
    
    const query = 'INSERT INTO device_groups (name, device_type, description) VALUES (?, ?, ?)';
    
    pool.execute(query, [name, device_type, description], (err, results) => {
        if (err) {
            console.error('Database insert error:', err);
            if (err.code === 'ER_DUP_ENTRY') {
                return res.status(400).json({ error: 'Group name already exists' });
            }
            return res.status(500).json({ error: 'Database insert failed' });
        }
        
        res.json({ 
            id: results.insertId, 
            name, 
            device_type, 
            description,
            message: 'Device group created successfully' 
        });
    });
});

app.put('/api/device-groups/:id', (req, res) => {
    const { id } = req.params;
    const { name, device_type, description } = req.body || {};
    if (!name || !device_type) return res.status(400).json({ error: 'name and device_type are required' });
    const sql = 'UPDATE device_groups SET name = ?, device_type = ?, description = ? WHERE id = ?';
    pool.execute(sql, [name, device_type, description || null, id], (err, result) => {
        if (err) {
            console.error('DB error (update group):', err);
            return res.status(500).json({ error: 'Failed to update group' });
        }
        res.json({ id: Number(id), name, device_type, description });
    });
});

app.delete('/api/device-groups/:id', (req, res) => {
    const { id } = req.params;
    const sql = 'DELETE FROM device_groups WHERE id = ?';
    pool.execute(sql, [id], (err, result) => {
        if (err) {
            console.error('DB error (delete group):', err);
            return res.status(500).json({ error: 'Failed to delete group' });
        }
        res.json({ id: Number(id), deleted: result.affectedRows > 0 });
    });
});

app.put('/api/device-groups/:id', (req, res) => {
    const { id } = req.params;
    const { name, device_type, description } = req.body;
    
    if (!name || !device_type) {
        return res.status(400).json({ error: 'Name and device_type are required' });
    }
    
    const query = 'UPDATE device_groups SET name = ?, device_type = ?, description = ? WHERE id = ?';
    
    pool.execute(query, [name, device_type, description, id], (err, results) => {
        if (err) {
            console.error('Database update error:', err);
            if (err.code === 'ER_DUP_ENTRY') {
                return res.status(400).json({ error: 'Group name already exists' });
            }
            return res.status(500).json({ error: 'Database update failed' });
        }
        
        if (results.affectedRows === 0) {
            return res.status(404).json({ error: 'Device group not found' });
        }
        
        res.json({ message: 'Device group updated successfully' });
    });
});

app.delete('/api/device-groups/:id', (req, res) => {
    const { id } = req.params;
    
    const query = 'DELETE FROM device_groups WHERE id = ?';
    
    pool.execute(query, [id], (err, results) => {
        if (err) {
            console.error('Database delete error:', err);
            return res.status(500).json({ error: 'Database delete failed' });
        }
        
        if (results.affectedRows === 0) {
            return res.status(404).json({ error: 'Device group not found' });
        }
        
        res.json({ message: 'Device group deleted successfully' });
    });
});

// Devices API
app.get('/api/devices', (req, res) => {
    const query = `
        SELECT d.*, dg.name as group_name, dg.device_type 
        FROM devices d 
        JOIN device_groups dg ON d.group_id = dg.id 
        ORDER BY d.created_at DESC
    `;
    
    pool.execute(query, (err, results) => {
        if (err) {
            console.error('Database query error:', err);
            return res.status(500).json({ error: 'Database query failed' });
        }
        res.json(results);
    });
});

app.post('/api/devices', (req, res) => {
    const { name, ip_address, group_id, description } = req.body;
    
    if (!name || !ip_address || !group_id) {
        return res.status(400).json({ error: 'Name, ip_address, and group_id are required' });
    }
    
    const query = 'INSERT INTO devices (name, ip_address, group_id, description) VALUES (?, ?, ?, ?)';
    
    pool.execute(query, [name, ip_address, group_id, description], (err, results) => {
        if (err) {
            console.error('Database insert error:', err);
            if (err.code === 'ER_DUP_ENTRY') {
                return res.status(400).json({ error: 'IP address already exists' });
            }
            return res.status(500).json({ error: 'Database insert failed' });
        }
        
        res.json({ 
            id: results.insertId, 
            name, 
            ip_address, 
            group_id, 
            description,
            message: 'Device created successfully' 
        });
    });
});

// Batch add devices
app.post('/api/devices/batch', (req, res) => {
    const { devices } = req.body;
    
    if (!devices || !Array.isArray(devices) || devices.length === 0) {
        return res.status(400).json({ error: 'Devices array is required' });
    }
    
    const query = 'INSERT INTO devices (name, ip_address, group_id, description) VALUES ?';
    const values = devices.map(device => [
        device.name,
        device.ip_address,
        device.group_id,
        device.description || ''
    ]);
    
    pool.query(query, [values], (err, results) => {
        if (err) {
            console.error('Database batch insert error:', err);
            return res.status(500).json({ error: 'Batch insert failed' });
        }
        
        res.json({ 
            message: `Successfully added ${results.affectedRows} devices`,
            added_count: results.affectedRows
        });
    });
});

app.put('/api/devices/:id', (req, res) => {
    const { id } = req.params;
    const { name, ip_address, group_id, description } = req.body;
    
    if (!name || !ip_address || !group_id) {
        return res.status(400).json({ error: 'Name, ip_address, and group_id are required' });
    }
    
    const query = 'UPDATE devices SET name = ?, ip_address = ?, group_id = ?, description = ? WHERE id = ?';
    
    pool.execute(query, [name, ip_address, group_id, description, id], (err, results) => {
        if (err) {
            console.error('Database update error:', err);
            if (err.code === 'ER_DUP_ENTRY') {
                return res.status(400).json({ error: 'IP address already exists' });
            }
            return res.status(500).json({ error: 'Database update failed' });
        }
        
        if (results.affectedRows === 0) {
            return res.status(404).json({ error: 'Device not found' });
        }
        
        res.json({ message: 'Device updated successfully' });
    });
});

app.delete('/api/devices/:id', (req, res) => {
    const { id } = req.params;
    
    const query = 'DELETE FROM devices WHERE id = ?';
    
    pool.execute(query, [id], (err, results) => {
        if (err) {
            console.error('Database delete error:', err);
            return res.status(500).json({ error: 'Database delete failed' });
        }
        
        if (results.affectedRows === 0) {
            return res.status(404).json({ error: 'Device not found' });
        }
        
        res.json({ message: 'Device deleted successfully' });
    });
});

// Tasks API
app.get('/api/tasks', (req, res) => {
    const query = `
        SELECT t.*, 
               COUNT(td.device_id) as device_count,
               COUNT(CASE WHEN td.status = 'completed' THEN 1 END) as completed_count,
               CASE 
                   WHEN COUNT(td.device_id) > 0 THEN 
                       ROUND((COUNT(CASE WHEN td.status = 'completed' THEN 1 END) * 100.0) / COUNT(td.device_id), 0)
                   ELSE 0 
               END as progress
        FROM tasks t 
        LEFT JOIN task_devices td ON t.id = td.task_id 
        GROUP BY t.id 
        ORDER BY t.created_at DESC
    `;
    
    pool.execute(query, (err, results) => {
        if (err) {
            console.error('Database query error:', err);
            return res.status(500).json({ error: 'Database query failed' });
        }
        res.json(results);
    });
});

app.post('/api/tasks', (req, res) => {
    const { name, type, strategy, command, device_ids } = req.body;
    
    if (!name || !type || !command || !device_ids || !Array.isArray(device_ids)) {
        return res.status(400).json({ error: 'Name, type, command, and device_ids are required' });
    }
    
    pool.getConnection((err, connection) => {
        if (err) {
            console.error('Connection error:', err);
            return res.status(500).json({ error: 'Database connection failed' });
        }
        
        connection.beginTransaction((err) => {
            if (err) {
                connection.release();
                return res.status(500).json({ error: 'Transaction start failed' });
            }
            
            // Insert task
            const taskQuery = 'INSERT INTO tasks (name, type, strategy, command, device_count) VALUES (?, ?, ?, ?, ?)';
            connection.execute(taskQuery, [name, type, strategy || 'parallel', command, device_ids.length], (err, taskResult) => {
                if (err) {
                    return connection.rollback(() => {
                        connection.release();
                        res.status(500).json({ error: 'Task creation failed' });
                    });
                }
                
                const taskId = taskResult.insertId;
                
                // Insert task-device relationships
                const deviceQuery = 'INSERT INTO task_devices (task_id, device_id) VALUES ?';
                const deviceValues = device_ids.map(deviceId => [taskId, deviceId]);
                
                connection.query(deviceQuery, [deviceValues], (err) => {
                    if (err) {
                        return connection.rollback(() => {
                            connection.release();
                            res.status(500).json({ error: 'Task-device relationship creation failed' });
                        });
                    }
                    
                    connection.commit((err) => {
                        if (err) {
                            return connection.rollback(() => {
                                connection.release();
                                res.status(500).json({ error: 'Transaction commit failed' });
                            });
                        }
                        
                        connection.release();
                        res.json({ 
                            id: taskId,
                            message: 'Task created successfully',
                            device_count: device_ids.length
                        });
                    });
                });
            });
        });
    });
});

// Get task details with device results
app.get('/api/tasks/:id', (req, res) => {
    const taskId = req.params.id;
    
    const taskQuery = `SELECT * FROM tasks WHERE id = ?`;
    const deviceQuery = `
        SELECT td.*, d.name as device_name, d.ip_address 
        FROM task_devices td 
        JOIN devices d ON td.device_id = d.id 
        WHERE td.task_id = ?
        ORDER BY d.name
    `;
    
    pool.execute(taskQuery, [taskId], (err, taskResults) => {
        if (err) {
            console.error('Database query error:', err);
            return res.status(500).json({ error: 'Database query failed' });
        }
        
        if (taskResults.length === 0) {
            return res.status(404).json({ error: 'Task not found' });
        }
        
        const task = taskResults[0];
        
        pool.execute(deviceQuery, [taskId], (err, deviceResults) => {
            if (err) {
                console.error('Database query error:', err);
                return res.status(500).json({ error: 'Database query failed' });
            }
            
            task.deviceResults = deviceResults;
            res.json(task);
        });
    });
});

// ---------------- SNMP (mocked) ----------------
// Get SNMP-like info for a device by ID (mock data; replace with real SNMP probing as needed)
app.get('/api/snmp/:id', (req, res) => {
    const { id } = req.params;
    const sql = `
        SELECT d.id, d.name, d.ip_address, d.group_id, g.name AS group_name, COALESCE(d.device_type, g.device_type) AS device_type
        FROM devices d
        JOIN device_groups g ON d.group_id = g.id
        WHERE d.id = ?
    `;
    pool.execute(sql, [id], (err, results) => {
        if (err) {
            console.error('SNMP query (device) error:', err);
            return res.status(500).json({ error: 'Database error' });
        }
        if (!results.length) return res.status(404).json({ error: 'Device not found' });
        const dev = results[0];

        // Mock SNMP data
        const now = new Date();
        const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
        const lastOctet = Number((dev.ip_address || '0.0.0.0').split('.').pop()) || rand(2, 200);
        const ifaceCount = Math.min(16, Math.max(3, lastOctet % 12 + 3));
        const interfaces = Array.from({ length: ifaceCount }).map((_, i) => {
            const idx = i + 1;
            const up = Math.random() > 0.1; // 90% up
            const speed = [100, 1000, 10000][rand(0, 2)];
            return {
                index: idx,
                name: `Gi0/${idx}`,
                adminStatus: 'up',
                operStatus: up ? 'up' : 'down',
                speedMbps: speed,
                inOctets: rand(10_000, 10_000_000),
                outOctets: rand(10_000, 10_000_000),
                inErrors: rand(0, up ? 2 : 10),
                outErrors: rand(0, up ? 2 : 10),
            };
        });

        const usedMem = rand(512, 4096);
        const totalMem = 8192;
        const cpu = rand(5, 70);
        const uptime = rand(60 * 60, 60 * 60 * 24 * 365);

        const payload = {
            device: dev,
            sys: {
                name: dev.name,
                descr: `${dev.device_type || 'NetworkOS'} ${rand(12, 16)}.${rand(0, 9)}.${rand(0, 9)} (${dev.group_name})`,
                objectId: '1.3.6.1.4.1.9.1.1234',
                upTimeSeconds: uptime,
            },
            resources: {
                cpuPercent: cpu,
                memory: { usedMB: usedMem, totalMB: totalMem, percent: Math.round((usedMem / totalMem) * 100) },
            },
            interfaces,
            stats: {
                upCount: interfaces.filter(x => x.operStatus === 'up').length,
                downCount: interfaces.filter(x => x.operStatus === 'down').length,
            },
            polledAt: now.toISOString(),
        };

        res.json(payload);
    });
});

// Get devices by group IDs
app.post('/api/devices/by-groups', (req, res) => {
    const { group_ids } = req.body;
    
    if (!group_ids || !Array.isArray(group_ids) || group_ids.length === 0) {
        return res.status(400).json({ error: 'Group IDs array is required' });
    }
    
    const placeholders = group_ids.map(() => '?').join(',');
    const query = `
        SELECT d.*, dg.name as group_name, dg.device_type 
        FROM devices d 
        JOIN device_groups dg ON d.group_id = dg.id 
        WHERE d.group_id IN (${placeholders})
        ORDER BY dg.name, d.name
    `;
    
    pool.execute(query, group_ids, (err, results) => {
        if (err) {
            console.error('Database query error:', err);
            return res.status(500).json({ error: 'Database query failed' });
        }
        res.json(results);
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

// ---------------- Device Groups ----------------
app.get('/api/device-groups', (req, res) => {
    const query = 'SELECT id, name, device_type, description, created_at FROM device_groups ORDER BY id DESC';
    pool.execute(query, (err, results) => {
        if (err) {
            console.error('DB error (device-groups):', err);
            return res.status(500).json({ error: 'Database error' });
        }
        res.json(results);
    });
});

app.post('/api/device-groups', (req, res) => {
    const { name, device_type, description } = req.body || {};
    if (!name || !device_type) return res.status(400).json({ error: 'name and device_type are required' });
    const sql = 'INSERT INTO device_groups (name, device_type, description) VALUES (?, ?, ?)';
    pool.execute(sql, [name, device_type, description || null], (err, result) => {
        if (err) {
            console.error('DB error (add group):', err);
            return res.status(500).json({ error: 'Failed to create group' });
        }
        res.json({ id: result.insertId, name, device_type, description });
    });
});

// ---------------- Devices ----------------
app.get('/api/devices', (req, res) => {
    const sql = `
        SELECT d.id, d.name, d.ip_address, d.group_id, d.device_type, d.description, g.name AS group_name
        FROM devices d
        JOIN device_groups g ON d.group_id = g.id
        ORDER BY d.id DESC
    `;
    pool.execute(sql, (err, results) => {
        if (err) {
            console.error('DB error (devices):', err);
            return res.status(500).json({ error: 'Database error' });
        }
        res.json(results);
    });
});

app.post('/api/devices/batch', (req, res) => {
    const { devices } = req.body || {};
    if (!Array.isArray(devices) || devices.length === 0) {
        return res.status(400).json({ error: 'devices array required' });
    }
    // Expect each: { name, ip_address, group_id, description }
    const insertSql = 'INSERT INTO devices (name, ip_address, group_id, device_type, description) VALUES (?, ?, ?, (SELECT device_type FROM device_groups WHERE id = ?), ?)';
    const tasks = devices.map(d => new Promise((resolve) => {
        // Use group_id twice (for value and subquery)
        pool.execute(insertSql, [d.name, d.ip_address, d.group_id, d.group_id, d.description || null], (err, result) => {
            if (err) {
                console.error('Insert device error for', d.ip_address, err.code);
                return resolve({ success: false, error: err.code || 'DB_ERROR', device: d });
            }
            resolve({ success: true, id: result.insertId, device: d });
        });
    }));
    Promise.all(tasks).then(results => {
        const added = results.filter(r => r.success).length;
        res.json({ added_count: added, results });
    });
});

app.post('/api/devices', (req, res) => {
    const d = req.body || {};
    if (!d.name || !d.ip_address || !d.group_id) {
        return res.status(400).json({ error: 'name, ip_address, group_id required' });
    }
    const insertSql = 'INSERT INTO devices (name, ip_address, group_id, device_type, description) VALUES (?, ?, ?, (SELECT device_type FROM device_groups WHERE id = ?), ?)';
    pool.execute(insertSql, [d.name, d.ip_address, d.group_id, d.group_id, d.description || null], (err, result) => {
        if (err) {
            console.error('Insert device error:', err);
            return res.status(500).json({ error: err.code || 'DB_ERROR' });
        }
        res.json({ id: result.insertId, ...d });
    });
});

app.put('/api/devices/:id', (req, res) => {
    const { id } = req.params;
    const d = req.body || {};
    if (!d.name || !d.ip_address || !d.group_id) {
        return res.status(400).json({ error: 'name, ip_address, group_id required' });
    }
    const sql = 'UPDATE devices SET name = ?, ip_address = ?, group_id = ?, device_type = (SELECT device_type FROM device_groups WHERE id = ?), description = ? WHERE id = ?';
    pool.execute(sql, [d.name, d.ip_address, d.group_id, d.group_id, d.description || null, id], (err, result) => {
        if (err) {
            console.error('Update device error:', err);
            return res.status(500).json({ error: err.code || 'DB_ERROR' });
        }
        res.json({ id: Number(id), ...d });
    });
});

app.delete('/api/devices/:id', (req, res) => {
    const { id } = req.params;
    const sql = 'DELETE FROM devices WHERE id = ?';
    pool.execute(sql, [id], (err, result) => {
        if (err) {
            console.error('Delete device error:', err);
            return res.status(500).json({ error: 'DB_ERROR' });
        }
        res.json({ id: Number(id), deleted: result.affectedRows > 0 });
    });
});

// ---------------- Tasks (mock minimal) ----------------
app.get('/api/tasks', (req, res) => {
    // Minimal in-memory fallback using DB table if exists
    const sql = 'SELECT id, name, type, strategy, command, device_count, status, progress, created_at, finished_at FROM tasks ORDER BY id DESC';
    pool.execute(sql, (err, results) => {
        if (err) {
            // If tasks table not present, return empty list gracefully
            console.warn('Tasks query error:', err.code);
            return res.json([]);
        }
        res.json(results);
    });
});

app.post('/api/tasks', (req, res) => {
    const { name, type, strategy, command, device_ids } = req.body || {};
    if (!name || !type || !strategy || !command || !Array.isArray(device_ids)) {
        return res.status(400).json({ error: 'invalid payload' });
    }
    const device_count = device_ids.length;
    const sql = 'INSERT INTO tasks (name, type, strategy, command, device_count, status, progress) VALUES (?, ?, ?, ?, ?, "running", 0)';
    pool.execute(sql, [name, type, strategy, command, device_count], (err, result) => {
        if (err) {
            console.error('Create task error:', err);
            return res.status(500).json({ error: 'Failed to create task' });
        }
        res.json({ id: result.insertId, name, type, strategy, command, device_count, status: 'running', progress: 0 });
    });
});

app.get('/api/tasks/:id', (req, res) => {
    const id = req.params.id;
    const sql = 'SELECT id, name, type, strategy, command, device_count, status, progress, created_at, finished_at FROM tasks WHERE id = ?';
    pool.execute(sql, [id], (err, results) => {
        if (err) {
            console.error('Get task error:', err);
            return res.status(500).json({ error: 'Failed to get task' });
        }
        if (!results.length) return res.status(404).json({ error: 'Not found' });
        // For demo, attach deviceResults as empty
        const task = results[0];
        task.deviceResults = [];
        res.json(task);
    });
});

app.listen(port, () => {
    console.log(`API server running at http://localhost:${port}`);
    console.log(`Health check: http://localhost:${port}/api/health`);
    console.log(`Device Groups API: http://localhost:${port}/api/device-groups`);
    console.log(`Devices API: http://localhost:${port}/api/devices`);
    console.log(`Tasks API: http://localhost:${port}/api/tasks`);
});

module.exports = app;
