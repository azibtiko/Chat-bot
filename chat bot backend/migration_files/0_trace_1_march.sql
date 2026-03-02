CREATE TABLE IF NOT EXISTS trace (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trace_code VARCHAR(255) NOT NULL UNIQUE,
    user_message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    category ENUM('Billing', 'Refund', 'Account_Access', 'Cancellation', 'General_inquiry') NOT NULL,
    response_time_ms INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);