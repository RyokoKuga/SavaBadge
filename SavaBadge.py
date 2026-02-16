import http.server
import socketserver
import webbrowser
import os
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / 'config.json'

def get_html_files():
    return [f.name for f in BASE_DIR.glob('*.html')]

def load_or_create_config():
    html_files = get_html_files()
    default_html = html_files[0] if html_files else "index.html"
    
    default_config = {
        "port": 8000,
        "target_html": default_html
    }

    try:
        if not CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            return default_config
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # JSON broken or inaccessible, fallback to default
        return default_config

def start_server():
    config = load_or_create_config()
    port = config.get("port", 8000)
    target = config.get("target_html", "index.html")

    os.chdir(BASE_DIR)
    
    Handler = http.server.SimpleHTTPRequestHandler
    url = f"http://localhost:{port}/{target}"

    # Reuse address to prevent "address already in use" errors during quick restarts
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
            print(f"--- Server Started ({sys.platform}) ---")
            print(f"Local URL: {url}")
            print("Press Ctrl+C to stop the server")
            
            webbrowser.open(url)
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98 or e.errno == 10048:
            print(f"Error: Port {port} is already in use.")
            print(f"Please change the 'port' in config.json and try again.")
        else:
            print(f"System Error: {e}")
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    start_server()