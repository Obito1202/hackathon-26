# Agent Tree Visualizer

A single-page React app that renders `display.json` as a tree diagram: the
main agent at the top, sub-agents branching below it, and tools as leaf
nodes. No build step — React, ReactDOM, and Babel are vendored locally and
loaded via plain `<script>` tags, and JSX is compiled in-browser at runtime.

## Files

- `index.html` — the app (markup, styles, and JSX all in one file)
- `display.json` — the tree data it renders (edit this to change the diagram)
- `vendor/` — local copies of React, ReactDOM, and Babel standalone (no CDN/internet required)

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
