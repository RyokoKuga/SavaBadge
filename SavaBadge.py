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
        return default_config

def save_config(config):
    """現在の設定をJSONファイルに保存する"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Warning: Could not update config.json: {e}")

def start_server():
    config = load_or_create_config()
    current_port = config.get("port", 8000)
    target = config.get("target_html", "index.html")

    os.chdir(BASE_DIR)
    Handler = http.server.SimpleHTTPRequestHandler
    
    # アドレスの再利用を許可
    socketserver.TCPServer.allow_reuse_address = True

    server_started = False
    
    # 空いているポートが見つかるまでループ（最大100回試行）
    for _ in range(100):
        try:
            with socketserver.TCPServer(("127.0.0.1", current_port), Handler) as httpd:
                # 実際に使用したポートが元の設定と異なる場合、JSONを更新
                if current_port != config.get("port"):
                    config["port"] = current_port
                    save_config(config)
                    print(f"Config updated: New port is {current_port}")

                url = f"http://localhost:{current_port}/{target}"
                print(f"--- Server Started ({sys.platform}) ---")
                print(f"Local URL: {url}")
                print("Press Ctrl+C to stop the server")
                
                webbrowser.open(url)
                server_started = True
                httpd.serve_forever()
                
        except OSError as e:
            # ポート使用中のエラーコード (Windows: 10048, Unix: 98)
            if e.errno in [98, 10048]:
                print(f"Port {current_port} is busy, trying {current_port + 1}...")
                current_port += 1
                continue
            else:
                print(f"System Error: {e}")
                break
        except KeyboardInterrupt:
            print("\nServer stopped.")
            break
        
        if server_started:
            break

if __name__ == "__main__":
    start_server()