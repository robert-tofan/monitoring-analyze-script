from datetime import datetime
import os

OUTPUT_DIR = './unit_test'
LOG_FILE_PATH = './logs.log'
CURRENT_TIME = datetime.now().strftime('%Y%m%d%H%M')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f'output_{CURRENT_TIME}.log')