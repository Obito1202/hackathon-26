import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from tree_view import render_tree_html

app = FastAPI(title="Agent Tree Visualizer API")

_VENDOR_DIR = os.path.join(os.path.dirname(__file__), "vendor")
app.mount("/vendor", StaticFiles(directory=_VENDOR_DIR), name="vendor")


@app.post("/visualize", response_class=HTMLResponse)
def visualize_tree(payload: dict):
    return render_tree_html(payload)
