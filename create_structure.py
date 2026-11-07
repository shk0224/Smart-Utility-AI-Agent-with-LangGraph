
from pathlib import Path

# Project root folder
BASE_DIR = Path(__file__).resolve().parent

# Project folders
folders = [
    "tools",
    "templates"
]

# Project files
files = [
    "app.py",
    "backend.py",
    "requirements.txt",
    ".env.example",
    "tools/__init__.py",
    "tools/age_tool.py",
    "tools/bmi_tool.py",
    "tools/date_tool.py",
    "tools/calculator_tool.py",
    "templates/index.html"
]

# Create folders
for folder in folders:
    (BASE_DIR / folder).mkdir(parents=True, exist_ok=True)

# Create files
for file in files:
    file_path = BASE_DIR / file
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch(exist_ok=True)

print("Project structure created successfully!")
