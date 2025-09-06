-- Create database
CREATE DATABASE IF NOT EXISTS network_delay_db;

-- Use database
USE network_delay_db;

-- Create delay data table
CREATE TABLE delay_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    slice VARCHAR(50) NOT NULL,
    src VARCHAR(50) NOT NULL,
    dst VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    delay DECIMAL(10,3) NOT NULL COMMENT 'Delay in milliseconds'
);

-- Create device groups table
CREATE TABLE IF NOT EXISTS device_groups (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    device_type VARCHAR(50) NOT NULL,
    description VARCHAR(255) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create devices table
CREATE TABLE IF NOT EXISTS devices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    group_id INT NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    description VARCHAR(255) DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_devices_group FOREIGN KEY (group_id) REFERENCES device_groups(id) ON DELETE CASCADE,
    UNIQUE KEY uniq_devices_ip (ip_address)
);

-- Optional: tasks table (basic tracking)
CREATE TABLE IF NOT EXISTS tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    strategy VARCHAR(50) NOT NULL,
    command TEXT NOT NULL,
    device_count INT NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    progress INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at DATETIME NULL
);