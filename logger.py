import logging
import sys
from datetime import datetime
from typing import Optional
import os

def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup a logger with specified configuration.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        format_string: Optional custom format string
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Default format
    if not format_string:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        try:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Could not create file handler: {str(e)}")
    
    return logger

def setup_app_logging(log_level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    """
    Setup application-wide logging configuration.
    
    Args:
        log_level: Logging level
        log_dir: Directory for log files
        
    Returns:
        Main application logger
    """
    # Create logs directory
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate log file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"chatbot_{timestamp}.log")
    
    # Setup main logger
    main_logger = setup_logger(
        name="chatbot_app",
        level=log_level,
        log_file=log_file
    )
    
    # Setup service loggers
    mistral_logger = setup_logger(
        name="mistral_service",
        level=log_level,
        log_file=log_file
    )
    
    qdrant_logger = setup_logger(
        name="qdrant_service", 
        level=log_level,
        log_file=log_file
    )
    
    # Log startup message
    main_logger.info("=" * 50)
    main_logger.info("Chatbot Application Starting")
    main_logger.info(f"Log Level: {log_level}")
    main_logger.info(f"Log File: {log_file}")
    main_logger.info("=" * 50)
    
    return main_logger

class CustomFilter(logging.Filter):
    """Custom logging filter for sensitive data."""
    
    def __init__(self, sensitive_keywords: list = None):
        super().__init__()
        self.sensitive_keywords = sensitive_keywords or [
            'api_key', 'password', 'token', 'secret', 'credential'
        ]
    
    def filter(self, record):
        """Filter out sensitive information from log records."""
        if hasattr(record, 'msg'):
            message = str(record.msg).lower()
            for keyword in self.sensitive_keywords:
                if keyword in message:
                    record.msg = record.msg.replace(
                        record.msg[record.msg.lower().find(keyword):],
                        f"{keyword}=***REDACTED***"
                    )
        return True

class PerformanceLogger:
    """Context manager for logging performance metrics."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting operation: {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is not None:
            self.logger.error(
                f"Operation failed: {self.operation} - "
                f"Duration: {duration:.2f}s - Error: {exc_val}"
            )
        else:
            self.logger.info(
                f"Operation completed: {self.operation} - "
                f"Duration: {duration:.2f}s"
            )

def log_function_call(logger: logging.Logger):
    """Decorator to log function calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"Calling function: {func_name}")
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Function {func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Function {func_name} failed: {str(e)}")
                raise
        return wrapper
    return decorator

class StreamlitLogHandler(logging.Handler):
    """Custom log handler for Streamlit applications."""
    
    def __init__(self):
        super().__init__()
        self.log_records = []
        self.max_records = 100  # Keep last 100 log records
    
    def emit(self, record):
        """Handle a log record."""
        try:
            # Format the record
            formatted_record = {
                'timestamp': datetime.fromtimestamp(record.created),
                'level': record.levelname,
                'logger': record.name,
                'message': self.format(record),
                'filename': record.filename,
                'lineno': record.lineno
            }
            
            # Add to records list
            self.log_records.append(formatted_record)
            
            # Maintain max records limit
            if len(self.log_records) > self.max_records:
                self.log_records.pop(0)
                
        except Exception:
            self.handleError(record)
    
    def get_logs(self, level: str = None, limit: int = None):
        """
        Get log records with optional filtering.
        
        Args:
            level: Filter by log level
            limit: Limit number of records
            
        Returns:
            List of log records
        """
        records = self.log_records
        
        if level:
            records = [r for r in records if r['level'] == level.upper()]
        
        if limit:
            records = records[-limit:]
        
        return records
    
    def clear_logs(self):
        """Clear all log records."""
        self.log_records.clear()

# Global Streamlit log handler instance
streamlit_handler = StreamlitLogHandler()

def add_streamlit_handler(logger: logging.Logger):
    """Add Streamlit handler to a logger."""
    if streamlit_handler not in logger.handlers:
        logger.addHandler(streamlit_handler)