@echo off
echo 🎨 Setting up Etsy Art Agent...

:: Check Python
python --version

:: Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

:: Activate and install
venv\Scripts\activate
python -m pip install --upgrade pip
pip install uv
pip install -r requirements.txt

:: Install agents-cli
echo 🔧 Installing agents-cli...
uvx google-agents-cli setup

:: Create directories
mkdir etsy_business_manager\data 2>nul
mkdir eval_results 2>nul

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo   1. venv\Scripts\activate
echo   2. set GEMINI_API_KEY=your-key
echo   3. adk web
echo   4. Open web_interface/index.html in your browser
pause
