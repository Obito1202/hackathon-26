# Agent Tree Visualizer

A single-page React app that renders `display.json` as a tree diagram: the
main agent at the top, sub-agents branching below it, and tools as leaf
nodes. No build step — React, ReactDOM, and Babel are vendored locally and
loaded via plain `<script>` tags, and JSX is compiled in-browser at runtime.

## Files

- `index.html` — static viewer app (markup, styles, and JSX all in one file)
- `display.json` — the tree data the static viewer renders (edit this to change the diagram)
- `vendor/` — local copies of React, ReactDOM, and Babel standalone (no CDN/internet required)
- `api.py` — FastAPI app exposing `POST /visualize` to render an arbitrary tree JSON on demand
- `tree_view.py` — shared HTML/CSS/JSX template used by `api.py` to build the response page

## Prerequisites

- A modern browser (Chrome, Firefox, Safari, Edge)
- Python 3 (or any static file server) — **required**, because the page
  `fetch()`s `display.json`, and browsers block `fetch` of local files when
  opened directly via `file://`

No npm install, no Node.js, no build tooling needed.

## Running it

From this `interface/` directory:

```bash
python3 -m http.server 8000
```

Then open **http://localhost:8000** in your browser.

Alternative static servers work the same way, e.g.:

```bash
npx serve .
# or
php -S localhost:8000
```

## Updating the diagram

Edit `display.json` and refresh the page — no rebuild required. Expected
shape:

```json
{
  "agent-id": "agent-main",
  "children": [
    { "agent-id": "agent-sub", "children": [
      { "tool-id": "tool-example" }
    ]}
  ]
}
```

- Nodes with `"agent-id"` can have `children` (agents or tools).
- Nodes with `"tool-id"` are always leaves (no `children`).
- The top-level node is styled as the main/orchestrator agent; nested
  `agent-id` nodes are styled as sub-agents; `tool-id` nodes are styled as
  tools.

If `display.json` is missing or fails to load, the page falls back to a
built-in example tree so it never renders blank.

## Troubleshooting

- **Blank page / tree not showing** — check the browser console. Most
  likely cause is opening `index.html` directly as a file instead of via a
  local server (see Prerequisites above).
- **Diagram looks stale** — hard-refresh the browser (the static server
  doesn't cache aggressively, but browsers sometimes do).

## Render-on-demand API

`api.py` is a separate FastAPI app (independent of the static viewer above)
that renders any posted tree JSON into a full HTML page.

### Run it

From this `interface/` directory (requires `fastapi` and `uvicorn`, already
in the repo's root `requirements.txt`):

```bash
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

### Use it

```bash
curl -X POST http://127.0.0.1:8000/visualize \
  -H "Content-Type: application/json" \
  -d @display.json \
  -o result.html
```

Open `result.html` in a browser (the server must still be running — the
page loads React/Babel from `/vendor`, served by the same app). The request
body must use the same shape as `display.json` (see above).

### Alternative: browser DevTools console

Navigate to `http://127.0.0.1:8000/docs` (same origin as the API), open the
console, and run:

```js
fetch('/visualize', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    "agent-id": "agent-main",
    "children": [
      { "agent-id": "sub-agent", "children": [ { "tool-id": "some-tool" } ] }
    ]
  })
})
  .then(r => r.text())
  .then(html => { document.open(); document.write(html); document.close(); });
```
