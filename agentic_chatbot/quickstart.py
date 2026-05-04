#!/usr/bin/env python3
"""
Quick Start Script for PathVancer Agentic Chatbot

This script helps you quickly set up and test the chatbot locally.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n📝 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main setup flow"""
    print("""
    🚀 PathVancer Agentic Chatbot - Quick Start
    =============================================
    """)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create venv
    venv_path = Path("venv")
    if not venv_path.exists():
        if not run_command(f"python -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Determine activation command
    activate_cmd = "venv\\Scripts\\activate" if sys.platform == "win32" else "source venv/bin/activate"
    
    # Install dependencies
    pip_cmd = f"{activate_cmd} && pip install -r requirements.txt" if sys.platform == "win32" else f"{activate_cmd} && pip install -r requirements.txt"
    
    print(f"\n📝 Installing dependencies...")
    print(f"   This may take 1-2 minutes...")
    
    if sys.platform == "win32":
        full_cmd = f"cmd /c \"{pip_cmd}\""
    else:
        full_cmd = f"bash -c '{pip_cmd}'"
    
    try:
        result = subprocess.run(full_cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ Dependencies installed - OK")
    except subprocess.CalledProcessError as e:
        print("❌ Dependency installation - FAILED")
        print(f"   Error: {e.stderr}")
        print("\n💡 Try: pip install -r requirements.txt")
        sys.exit(1)
    
    # Setup .env
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        print("\n📝 Setting up environment file...")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print(f"✅ Created .env file")
            print(f"⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file exists")
    
    # Check OpenAI key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("\n⚠️  OPENAI_API_KEY not set!")
        print("   Please add it to .env file:")
        print("   OPENAI_API_KEY=sk-your-key-here")
    else:
        print("✅ OPENAI_API_KEY configured")
    
    # Test import
    print("\n📝 Testing imports...")
    try:
        if sys.platform == "win32":
            result = subprocess.run(f"cmd /c \"{activate_cmd} && python -c \\\"import langchain; import fastapi; print('✅ Imports OK')\\\"\"", shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(f"bash -c '{activate_cmd} && python -c \"import langchain; import fastapi; print(\\\"✅ Imports OK\\\")\"'", shell=True, check=True, capture_output=True, text=True)
        print(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        print("❌ Import test failed")
        print(e.stderr)
    
    # Ready to run
    print(f"""
    
    ✅ Setup Complete!
    
    Next steps:
    
    1. Edit .env with your OPENAI_API_KEY
    
    2. Run the server:
       {activate_cmd}
       python -m uvicorn app.main:app --reload
    
    3. Open browser:
       http://localhost:8000/docs
    
    4. Test the chat endpoint:
       curl -X POST http://localhost:8000/chat \\
         -H "Content-Type: application/json" \\
         -d '{{"message": "Hello!", "session_id": "test"}}'
    
    5. Deploy to cloud:
       - Render: See README.md
       - AWS: See deploy-aws.sh
       - Docker: docker build -t pathvancer-chatbot .
    
    📚 Documentation:
       - README.md - Setup & deployment
       - ARCHITECTURE.md - System design
       - FRONTEND_INTEGRATION.md - Frontend examples
       - PROJECT_SUMMARY.md - Complete overview
    
    Need help? Check the docs or see client_example.py for usage examples.
    """)

if __name__ == "__main__":
    main()
