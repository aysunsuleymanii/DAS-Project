import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import time
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to run the main process
def scheduled_task():
    logger.info(f"Running scheduled task at {datetime.now()}")
    start_time = time.time()

    try:
        # Use subprocess to run 'first_version.py' as an external script
        subprocess.run(['python3', '/Users/aysunsuleymanturk/Desktop/FINAL/Homework1/first_version.py'], check=True)
    except Exception as e:
        logger.error(f"Error running scheduled task: {e}")

    end_time = time.time()
    logger.info(f"Task completed in {end_time - start_time:.2f} seconds.")

# Setup the scheduler
scheduler = BlockingScheduler()

# Schedule the task to run daily at a specific time (e.g., 8 AM every day)
scheduler.add_job(scheduled_task, 'cron', hour=8, minute=0, second=0)

logger.info("Scheduler started...")

# Start the scheduler
scheduler.start()
