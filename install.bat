@echo off

rem Create a virtual environment if it doesn't exist
if not exist ".\venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

rem Activate the virtual environment
call .\venv\Scripts\activate.bat

rem Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r .\requirements.txt

echo Setup complete.