import streamlit.web.cli as stcli
import sys
import os
import threading
import time
import webbrowser

def open_browser():
    time.sleep(1)  # Wait a moment for the server to start
    webbrowser.open_new("http://localhost:8501")

def main():
    threading.Thread(target=open_browser, daemon=True).start()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(base_dir, "app.py")

    sys.argv = ["streamlit", "run", app_path, "--server.headless=true","--server.port=8501"]
    sys.exit(stcli.main())
    
if __name__ == "__main__":
    main()