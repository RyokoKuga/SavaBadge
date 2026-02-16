# SavaBadge

A minimal Python script to host and preview HTML files locally. 

<img src="Image/Card.png" width="600px">

## Features
* **Auto-Preview**: Opens your browser to the target HTML file automatically.
* **Auto-Config**: Creates a `config.json` on the first run.
* **No Dependencies**: Uses only Python standard libraries.

## Quick Start
Place `SavaBadge.py` in your project folder and run it.

## Configuration
Customize settings in `config.json`:
```json
{
    "port": 8000,
    "target_html": "index.html"
}
```
* port: Local server port.
* target_html: File to open by default.
