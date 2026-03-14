import os
import sys

# Add the backend directory to sys.path so absolute imports in backend work correctly
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.insert(0, backend_path)

from backend.main import app
