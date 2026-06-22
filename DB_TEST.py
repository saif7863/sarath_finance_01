from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).parent / ".env"

print("ENV FILE EXISTS:", env_path.exists())
print("ENV PATH:", env_path)

load_dotenv(env_path)

print("DATABASE_URL =", os.getenv("DATABASE_URL"))

import db