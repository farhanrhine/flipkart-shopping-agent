# 🔍 Logger & Custom Exception Usage Guide

## 📚 Table of Contents

1. [Basic Pattern](#basic-pattern)
2. [Logger Usage Examples](#logger-usage-examples)
3. [Custom Exception Usage](#custom-exception-usage)
4. [Real-World Examples](#real-world-examples)
5. [Best Practices](#best-practices)

---

## 🎯 Basic Pattern

### Step 1: Import at the top of your file

```python
import sys
from src.utils.logger import logger
from src.utils.custom_exception import CustomException
```

### Step 2: Use logger throughout your code

```python
# Log different levels of information
logger.info("This is informational")
logger.warning("This is a warning")
logger.error("This is an error")
logger.debug("This is debug info")
```

### Step 3: Wrap risky code in try-except blocks

```python
try:
    # Your code that might fail
    result = some_function()
    logger.info("Operation successful")
except Exception as e:
    logger.error(f"Operation failed: {str(e)}")
    raise CustomException("Detailed error message", sys)
```

---

## 📝 Logger Usage Examples

### Example 1: Basic Function Logging

```python
import sys
from src.utils.logger import logger
from src.utils.custom_exception import CustomException

def add_numbers(a, b):
    """Add two numbers with logging"""
    logger.info(f"Starting addition: {a} + {b}")
    
    try:
        result = a + b
        logger.info(f"Addition successful: {a} + {b} = {result}")
        return result
    except Exception as e:
        logger.error(f"Addition failed: {str(e)}")
        raise CustomException(f"Failed to add {a} and {b}", sys)
```

### Example 2: File Operations

```python
import sys
from src.utils.logger import logger
from src.utils.custom_exception import CustomException

def read_config_file(filepath):
    """Read configuration file with proper logging"""
    logger.info(f"Attempting to read config file: {filepath}")
    
    try:
        with open(filepath, 'r') as f:
            data = f.read()
        logger.info(f"Successfully read config file: {filepath}")
        return data
    except FileNotFoundError as e:
        logger.error(f"Config file not found: {filepath}")
        raise CustomException(f"Configuration file '{filepath}' not found", sys)
    except Exception as e:
        logger.error(f"Error reading config file: {str(e)}")
        raise CustomException(f"Failed to read config file '{filepath}'", sys)
```

### Example 3: API/Database Operations

```python
import sys
from src.utils.logger import logger
from src.utils.custom_exception import CustomException

def fetch_product_data(product_id):
    """Fetch product data from database/API"""
    logger.info(f"Fetching product data for ID: {product_id}")
    
    try:
        # Simulate API call
        logger.debug(f"Connecting to database...")
        # product_data = db.get_product(product_id)
        
        logger.info(f"Successfully fetched product: {product_id}")
        return product_data
    except ConnectionError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise CustomException("Database connection error", sys)
    except Exception as e:
        logger.error(f"Failed to fetch product {product_id}: {str(e)}")
        raise CustomException(f"Product fetch failed for ID: {product_id}", sys)
```

---

## 🚨 Custom Exception Usage

### When to Use Custom Exception?

Use `CustomException` when:

1. ❌ An operation fails and you want detailed error tracking
2. ❌ You need to know exactly which file and line caused the error
3. ❌ You want to provide context-specific error messages
4. ❌ You're catching and re-raising exceptions with more context

### Pattern

```python
try:
    # risky operation
    result = do_something()
except SpecificError as e:
    logger.error(f"Specific error occurred: {str(e)}")
    raise CustomException("User-friendly error message", sys)
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise CustomException("General error message", sys)
```

---

## 🌟 Real-World Examples

### Example 1: Data Processing Pipeline

```python
import sys
import pandas as pd
from src.utils.logger import logger
from src.utils.custom_exception import CustomException

def process_product_data(csv_path):
    """Process product data from CSV"""
    logger.info(f"Starting data processing pipeline for: {csv_path}")
    
    try:
        # Step 1: Load data
        logger.info("Step 1: Loading CSV data...")
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} rows of data")
        
        # Step 2: Clean data
        logger.info("Step 2: Cleaning data...")
        df = df.dropna()
        logger.info(f"After cleaning: {len(df)} rows remaining")
        
        # Step 3: Transform data
        logger.info("Step 3: Transforming data...")
        df['price'] = df['price'].astype(float)
        logger.info("Data transformation complete")
        
        logger.info("✅ Data processing pipeline completed successfully")
        return df
        
    except FileNotFoundError as e:
        logger.error(f"CSV file not found: {csv_path}")
        raise CustomException(f"Data file '{csv_path}' does not exist", sys)
    except pd.errors.EmptyDataError as e:
        logger.error(f"CSV file is empty: {csv_path}")
        raise CustomException(f"Data file '{csv_path}' is empty", sys)
    except Exception as e:
        logger.error(f"Data processing failed: {str(e)}")
        raise CustomException("Data processing pipeline failed", sys)
```

### Example 2: Machine Learning Model

```python
import sys
from src.utils.logger import logger
from src.utils.custom_exception import CustomException

class ProductRecommender:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None
        logger.info(f"Initializing ProductRecommender with model: {model_path}")
    
    def load_model(self):
        """Load the ML model"""
        logger.info(f"Loading model from: {self.model_path}")
        
        try:
            # Simulate model loading
            # self.model = joblib.load(self.model_path)
            logger.info("✅ Model loaded successfully")
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {self.model_path}")
            raise CustomException(f"Model file '{self.model_path}' not found", sys)
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            raise CustomException("Failed to load ML model", sys)
    
    def predict(self, user_id, product_ids):
        """Make predictions"""
        logger.info(f"Making predictions for user: {user_id}")
        logger.debug(f"Product IDs: {product_ids}")
        
        try:
            if self.model is None:
                logger.warning("Model not loaded, loading now...")
                self.load_model()
            
            # predictions = self.model.predict(product_ids)
            logger.info(f"✅ Predictions generated for user {user_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction failed for user {user_id}: {str(e)}")
            raise CustomException(f"Prediction failed for user {user_id}", sys)
```

### Example 3: Web Scraping

```python
import sys
import requests
from src.utils.logger import logger
from src.utils.custom_exception import CustomException

def scrape_flipkart_product(url):
    """Scrape product details from Flipkart"""
    logger.info(f"Starting to scrape product: {url}")
    
    try:
        # Step 1: Send request
        logger.info("Sending HTTP request...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        logger.info(f"Response received: Status {response.status_code}")
        
        # Step 2: Parse HTML
        logger.info("Parsing HTML content...")
        # soup = BeautifulSoup(response.content, 'html.parser')
        
        # Step 3: Extract data
        logger.info("Extracting product data...")
        # product_data = extract_product_info(soup)
        
        logger.info("✅ Product scraped successfully")
        return product_data
        
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timeout for URL: {url}")
        raise CustomException(f"Request timed out for {url}", sys)
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {response.status_code}: {url}")
        raise CustomException(f"HTTP error while scraping {url}", sys)
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        raise CustomException(f"Failed to scrape product from {url}", sys)
```

---

## ✅ Best Practices

### 1. **Always Import at the Top**

```python
# ✅ GOOD
import sys
from src.utils.logger import logger
from src.utils.custom_exception import CustomException

def my_function():
    logger.info("Starting...")
```

```python
# ❌ BAD
def my_function():
    from src.utils.logger import logger  # Don't import inside functions
    logger.info("Starting...")
```

### 2. **Log at Different Stages**

```python
def complex_operation():
    logger.info("Starting complex operation...")  # Start
    
    logger.debug("Step 1: Initialization")  # Debug details
    # ... code ...
    
    logger.info("Step 2: Processing data")  # Progress
    # ... code ...
    
    logger.warning("Step 3: Found potential issue")  # Warnings
    # ... code ...
    
    logger.info("✅ Complex operation completed")  # Success
```

### 3. **Use Descriptive Error Messages**

```python
# ✅ GOOD - Specific and helpful
raise CustomException(f"Failed to process order {order_id} for user {user_id}", sys)

# ❌ BAD - Too vague
raise CustomException("Error occurred", sys)
```

### 4. **Log Before Raising Exception**

```python
# ✅ GOOD - Log first, then raise
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {str(e)}")  # Log the error
    raise CustomException("Detailed message", sys)  # Then raise
```

### 5. **Use Try-Except for External Operations**

Operations that should be wrapped in try-except:

- 📁 File operations (read/write)
- 🌐 API calls
- 🗄️ Database queries
- 🔢 Type conversions
- 📦 External library calls
- 🌍 Network requests

### 6. **Log Levels Guide**

```python
logger.debug("Detailed debugging info")      # Development only
logger.info("Normal operation messages")     # General info
logger.warning("Something unexpected")       # Potential issues
logger.error("Error occurred")               # Errors that need attention
logger.critical("System failure")            # Critical failures
```

---

## 📁 File Structure Pattern

```
your_project/
├── src/
│   ├── utils/
│   │   ├── logger.py           # ✅ Logger utility
│   │   └── custom_exception.py # ✅ Custom exception
│   ├── data_processing/
│   │   └── processor.py        # Import and use logger + exception
│   ├── models/
│   │   └── recommender.py      # Import and use logger + exception
│   └── api/
│       └── routes.py           # Import and use logger + exception
├── logs/
│   └── log_2026-01-28.log      # Auto-generated log files
└── main.py                     # Import and use logger + exception
```

---

## 🎓 Quick Reference

### Minimal Template for Any File

```python
import sys
from src.utils.logger import logger
from src.utils.custom_exception import CustomException

def your_function():
    logger.info("Function started")
    
    try:
        # Your code here
        result = do_something()
        logger.info("Function completed successfully")
        return result
    except Exception as e:
        logger.error(f"Function failed: {str(e)}")
        raise CustomException("Descriptive error message", sys)
```

---

**Remember:**

- 📝 **Logger** = Track what's happening (info, warnings, errors)
- 🚨 **CustomException** = Handle errors with detailed context
- 🔄 **Pattern** = Import → Log → Try-Except → Log Error → Raise Exception

Happy coding! 🚀
