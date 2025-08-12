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