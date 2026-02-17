import os
import tkinter as tk
from tkinter import filedialog, messagebox
import locale

def get_system_lang():
    """OSの言語設定を確認し、日本語でなければ 'en' を返す"""
    try:
        lang = locale.getdefaultlocale()[0]
        return 'ja' if lang and lang.startswith('ja') else 'en'
    except:
        return 'en'

def create_launcher_script():
    lang = get_system_lang()
    
    # メッセージの定義（日本語・英語切り替え）
    msgs = {
        'ja': {
            'step1': "手順 1: プロジェクトのルートディレクトリを選択してください。",
            'step2': "手順 2: 最初に開くHTMLファイルを選択してください。",
            'err_title': "エラー",
            'err_path': "HTMLファイルはルートディレクトリ内にある必要があります。",
            'done_title': "完了",
            'done_msg': "作成完了: {}\n\nこのファイルをダブルクリックするとサーバーが起動します。",
            'status': "サーバー起動中... (Ctrl+C で終了)"
        },
        'en': {
            'step1': "Step 1: Select the project root directory.",
            'step2': "Step 2: Select the HTML file to open first.",
            'err_title': "Error",
            'err_path': "The HTML file must be inside the root directory.",
            'done_title': "Done",
            'done_msg': "Created: {}\n\nDouble-click this file to start the server.",
            'status': "Server is running... (Press Ctrl+C to stop)"
        }
    }[lang]

    root = tk.Tk()
    root.withdraw()
    
    # 1. ディレクトリ選択
    messagebox.showinfo("Step 1", msgs['step1'])
    base_dir = filedialog.askdirectory()
    if not base_dir:
        return

    # 2. ファイル選択
    messagebox.showinfo("Step 2", msgs['step2'])
    html_file_path = filedialog.askopenfilename(
        initialdir=base_dir,
        filetypes=[("HTML files", "*.html;*.htm")]
    )
    if not html_file_path:
        return

    # パス計算
    try:
        # 相対パスを取得し、スラッシュに統一
        relative_html_path = os.path.relpath(html_file_path, base_dir).replace('\\', '/')
    except ValueError:
        messagebox.showerror(msgs['err_title'], msgs['err_path'])
        return

    # 3. 生成するスクリプトのテンプレート
    # f-stringの二重中括弧による混乱を避けるため、format()を使用
    script_template = """import http.server
import socketserver
import webbrowser
import os
import threading
import time
import sys

# 実行ファイルがある場所を基準にする
BASE_DIR = os.path.dirname(os.path.abspath(__file__)).replace('\\\\', '/')
TARGET_HTML = "{html_path}"
START_PORT = 8000
MAX_PORT = 8100

def start_server():
    os.chdir(BASE_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    
    current_port = START_PORT
    httpd = None
    
    # ポートが空くまで探索
    while current_port <= MAX_PORT:
        try:
            httpd = socketserver.TCPServer(("", current_port), handler)
            break
        except OSError:
            current_port += 1
    
    if httpd:
        url = f"http://localhost:{{current_port}}/{{TARGET_HTML}}"
        print(f"--- Local Server Started ---")
        print(f"URL: {{url}}")
        print(f"Root: {{BASE_DIR}}")
        
        # サーバー起動を待ってブラウザを開く
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        httpd.serve_forever()
    else:
        print(f"Error: Could not find an available port.")

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    print("{status_msg}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\nShutting down...")
        sys.exit()
"""

    output_content = script_template.format(
        html_path=relative_html_path,
        status_msg=msgs['status']
    )

    # 4. 選択されたディレクトリ内に保存
    output_filename = "run_app.py"
    output_path = os.path.join(base_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_content.strip())
        messagebox.showinfo(msgs['done_title'], msgs['done_msg'].format(output_path))
    except Exception as e:
        messagebox.showerror(msgs['err_title'], f"Failed to save file: {e}")

if __name__ == "__main__":
    create_launcher_script()