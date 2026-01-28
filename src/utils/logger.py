import logging # core logger 
import os  # create folder 
from datetime import datetime # timestamp logs

# create logs dir if exist so dont create new
Log_DIR = "logs"
os.makedirs(Log_DIR, exist_ok=True)

# dynamic log file per day
LOG_FILE = os.path.join(Log_DIR, f"log_{datetime.now().strftime('%Y-%m-%d')}.log")

# config logging for globally 
logging.basicConfig(filename=LOG_FILE, format="[%(asctime)s] %(levelname)s - %(message)s", level=logging.INFO)

# create reuseable logger obj
logger = logging.getLogger("Project_logger")