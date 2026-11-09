import os
# os is a Python module that lets your program interact with things related to the operating system.
# Here, we're going to use it to read an environment variable.
from dotenv import load_dotenv
# Allows Python to read variables stored in a .env file

load_dotenv()
# Look for a .env file and load the variables inside it.

SECRET_KEY = os.getenv("SECRET_KEY")
# Gets the secret key from the file; if not found returns none

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured")
# Check that the key exists

ALGORITHM = "HS256"
# Tells the JWT system: "Use HS256 when creating and verifying JWTs."
# Method used to sign the JWT