#!/usr/bin/env python3
"""
Generate 24-hour network delay data for different slices
Reads actual node names from JSON files and inserts data into MySQL database
"""

import mysql.connector
import random
from datetime import datetime, timedelta
import json
import os
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Change this to your MySQL username
    'password': '',  # Will be prompted for input
    'database': 'network_delay_db'
}

def get_database_config():
    """Get database configuration with user input if needed"""
    config = DB_CONFIG.copy()
    
    print("Database Connection Configuration")
    print("-" * 40)
    
    # Get user input for database credentials
    host = input(f"MySQL Host (default: {config['host']}): ").strip()
    if host:
        config['host'] = host
    
    user = input(f"MySQL Username (default: {config['user']}): ").strip()
    if user:
        config['user'] = user
    
    password = input("MySQL Password: ").strip()
    if password:
        config['password'] = password
    elif not config['password']:
        # If no password in config and none provided, prompt again
        config['password'] = input("MySQL Password (required): ").strip()
    
    database = input(f"Database Name (default: {config['database']}): ").strip()
    if database:
        config['database'] = database
    
    return config

# Slice configurations with delay ranges
SLICE_CONFIGS = {
    'eMBB-5G': {
        'delay_min': 10,
        'delay_max': 20,
        'json_file': '../public/mock/slice/eMBB-5G.json'
    },
    'eMBB-video': {
        'delay_min': 20,
        'delay_max': 35,
        'json_file': '../public/mock/slice/eMBB-video.json'
    },
    'mMTC-iot': {
        'delay_min': 40,
        'delay_max': 60,
        'json_file': '../public/mock/slice/mMTC-iot.json'
    },
    'URLLC-automotive': {
        'delay_min': 1,
        'delay_max': 5,
        'json_file': '../public/mock/slice/URLLC-automotive.json'
    },
    'URLLC-industrial': {
        'delay_min': 0.5,
        'delay_max': 2.5,
        'json_file': '../public/mock/slice/URLLC-industrial.json'
    },
    'physical-network': {
        'delay_min': 5,
        'delay_max': 13,
        'json_file': '../public/mock/slice/physical-network.json'
    }
}

def load_slice_connections(slice_name, config):
    """Load actual connections from JSON files and extract all node pairs"""
    json_file = config['json_file']
    
    # 构建绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, json_file)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 构建节点ID映射
        node_map = {}
        if 'cities' in data:
            for city in data['cities']:
                if 'id' in city:
                    # 对于 physical-network.json，ID可能是数字，需要转换为字符串
                    node_id = str(city['id'])
                    node_map[city['id']] = node_id  # 数字ID -> 字符串ID
                    node_map[node_id] = node_id     # 字符串ID -> 字符串ID
        
        # 提取所有连接对
        connections = []
        if 'connections' in data:
            for conn in data['connections']:
                if 'points' in conn and len(conn['points']) >= 2:
                    points = conn['points']
                    
                    # 如果只有2个点，直接连接
                    if len(points) == 2:
                        src_id = node_map.get(points[0], str(points[0]))
                        dst_id = node_map.get(points[1], str(points[1]))
                        connections.append((src_id, dst_id))
                    
                    # 如果有3个以上点，生成所有两两组合
                    elif len(points) > 2:
                        for i in range(len(points)):
                            for j in range(i + 1, len(points)):
                                src_id = node_map.get(points[i], str(points[i]))
                                dst_id = node_map.get(points[j], str(points[j]))
                                connections.append((src_id, dst_id))
        
        print(f"Loaded {len(connections)} connections for {slice_name}")
        print(f"Sample connections: {connections[:5]}{'...' if len(connections) > 5 else ''}")
        return connections
    
    except FileNotFoundError:
        print(f"Warning: JSON file not found for {slice_name}: {json_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {slice_name}: {e}")
        return []
    except Exception as e:
        print(f"Error loading connections for {slice_name}: {e}")
        return []

def load_slice_nodes(slice_name, config):
    """Load actual node IDs from JSON files"""
    json_file = config['json_file']
    
    # 构建绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, json_file)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = []
        if 'cities' in data:
            for city in data['cities']:
                # 优先使用 id 字段作为节点标识，避免中文乱码
                if 'id' in city:
                    nodes.append(str(city['id']))  # 确保是字符串类型
                elif 'name' in city:
                    nodes.append(city['name'])
        
        print(f"Loaded {len(nodes)} nodes for {slice_name}: {nodes[:5]}{'...' if len(nodes) > 5 else ''}")
        return nodes
    
    except FileNotFoundError:
        print(f"Warning: JSON file not found for {slice_name}: {json_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {slice_name}: {e}")
        return []
    except Exception as e:
        print(f"Error loading nodes for {slice_name}: {e}")
        return []

def connect_to_database(config=None):
    """Connect to MySQL database"""
    if config is None:
        config = DB_CONFIG
    
    try:
        print(f"Connecting to MySQL at {config['host']} as {config['user']}...")
        connection = mysql.connector.connect(**config)
        print("Database connection successful!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        if err.errno == 1045:
            print("\nThis is an authentication error. Please check:")
            print("1. Username is correct")
            print("2. Password is correct")
            print("3. User has access to the database")
        elif err.errno == 1049:
            print(f"\nDatabase '{config['database']}' does not exist.")
            print("Please run the init.sql script first to create the database.")
        return None

def clear_existing_data(connection):
    """Clear existing data from delay_data table"""
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM delay_data")
        affected_rows = cursor.rowcount
        connection.commit()
        print(f"Cleared {affected_rows} existing records from delay_data table")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error clearing data: {err}")

def generate_delay_data(slice_name, connections, delay_config, timestamp):
    """Generate delay data for all connections in a slice"""
    delay_records = []
    
    for src_node, dst_node in connections:
        # Generate random delay within the specified range
        delay = random.uniform(delay_config['delay_min'], delay_config['delay_max'])
        delay_records.append((slice_name, src_node, dst_node, timestamp, round(delay, 3)))
    
    return delay_records

def insert_batch_data(connection, data_batch):
    """Insert a batch of data into the database"""
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO delay_data (slice, src, dst, timestamp, delay) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(query, data_batch)
        connection.commit()
        print(f"Inserted {len(data_batch)} records at {data_batch[0][3]}")
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
    finally:
        cursor.close()

def generate_24_hour_data():
    """Generate 24 hours of delay data (one data point every 30 seconds)"""
    # Get database configuration
    db_config = get_database_config()
    
    connection = connect_to_database(db_config)
    if not connection:
        return
    
    try:
        # Clear existing data first
        print("Clearing existing data...")
        clear_existing_data(connection)
        
        # Load connections for all slices
        slice_connections = {}
        print("\nLoading connection data from JSON files...")
        for slice_name, config in SLICE_CONFIGS.items():
            connections = load_slice_connections(slice_name, config)
            if connections:
                slice_connections[slice_name] = connections
            else:
                print(f"Warning: No connections loaded for {slice_name}, skipping this slice")
        
        if not slice_connections:
            print("Error: No slice connection data loaded. Please check JSON files.")
            return
        
        print(f"\nSuccessfully loaded {len(slice_connections)} slices")
        for slice_name, connections in slice_connections.items():
            print(f"  - {slice_name}: {len(connections)} connections")
        
        # Start time: 2025-01-01 00:00:00
        start_time = datetime(2025, 1, 1, 0, 0, 0)
        current_time = start_time
        
        # 24 hours * 60 minutes * 2 (every 30 seconds) = 2880 data points
        total_data_points = 24 * 60 * 2
        
        print(f"\nGenerating {total_data_points} data points over 24 hours...")
        print("Each data point represents 30 seconds of time")
        
        for i in range(total_data_points):
            data_batch = []
            
            # Generate data for all slices at this timestamp
            for slice_name, connections in slice_connections.items():
                config = SLICE_CONFIGS[slice_name]
                delay_records = generate_delay_data(slice_name, connections, config, current_time)
                if delay_records:
                    data_batch.extend(delay_records)
            
            # Insert batch for this timestamp
            if data_batch:
                insert_batch_data(connection, data_batch)
            
            # Move to next timestamp (30 seconds later)
            current_time += timedelta(seconds=30)
            
            # Progress indicator
            if (i + 1) % 120 == 0:  # Every hour (120 * 30 seconds = 1 hour)
                hours_completed = (i + 1) // 120
                print(f"Progress: {hours_completed}/24 hours completed")
        
        total_connections = sum(len(connections) for connections in slice_connections.values())
        print(f"\nData generation completed!")
        print(f"Total records should be: {total_data_points * total_connections}")
        print(f"Records per slice per time point:")
        for slice_name, connections in slice_connections.items():
            print(f"  - {slice_name}: {len(connections)} records per time point")
        
        # Display summary statistics
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM delay_data")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("""
        SELECT slice, COUNT(*) as count, 
               ROUND(AVG(delay), 3) as avg_delay,
               ROUND(MIN(delay), 3) as min_delay,
               ROUND(MAX(delay), 3) as max_delay
        FROM delay_data 
        GROUP BY slice
        """)
        
        print(f"\nActual total records inserted: {total_records}")
        print("\nSummary by slice:")
        print("Slice".ljust(20) + "Count".ljust(10) + "Avg Delay".ljust(12) + "Min Delay".ljust(12) + "Max Delay")
        print("-" * 66)
        
        for row in cursor.fetchall():
            slice_name, count, avg_delay, min_delay, max_delay = row
            print(f"{slice_name:<20} {count:<10} {avg_delay:<12} {min_delay:<12} {max_delay}")
        
        cursor.close()
        
    except Exception as e:
        print(f"Error during data generation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        connection.close()

if __name__ == "__main__":
    print("Network Delay Data Generator")
    print("=" * 50)
    
    # Check if user wants to proceed
    response = input("This will generate 24 hours of delay data. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        exit()
    
    generate_24_hour_data()
