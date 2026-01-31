# import sys 
# from src.utils.custom_exception import CustomException
# from src.utils.logger import logger

# # Test logger - this will run first
# logger.info("Starting the application...")
# logger.info("Testing division operation")

# try: 
#     x = 1/0
#     logger.info("Division successful")
# except Exception as e:
#     logger.error(f"An error occurred: {str(e)}")
#     raise CustomException("Division failed", sys)