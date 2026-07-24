# Agent Tree Widget

A drop-in, client-side-only React widget that renders an agent/tool tree
as a topology diagram (main agent → sub-agents → tools). No backend, no
build step, no bundler — works by just including two script tags plus this
widget's script tag on any HTML page.

## Files

```
agent-tree-widget/
├── tree-widget.js                        the widget (only file specific to this)
├── demo.html                             a working example you can open directly
└── vendor/
    ├── react.production.min.js           React (required dependency)
    └── react-dom.production.min.js       ReactDOM (required dependency)
```

To use this in another project, copy the whole `agent-tree-widget/` folder
(or just `tree-widget.js` + `vendor/`) next to your page.

## Quick test

Double-click `demo.html` (or drag it into a browser tab) and click the
button. No server required — it works from a `file://` URL.

## Usage in your own page

```html
<div id="tree-container"></div>

<script src="vendor/react.production.min.js"></script>
<script src="vendor/react-dom.production.min.js"></script>
<script src="tree-widget.js"></script>
<script>
  var treeData = {
    "agent-id": "agent-main",
    "children": [
      { "agent-id": "agent-research", "children": [
        { "tool-id": "tool-web-search" }
      ]},
      { "tool-id": "tool-general-assistant" }
    ]
  };

  AgentTreeWidget.render(document.getElementById("tree-container"), treeData);
</script>
```

Load order matters: React and ReactDOM must load **before** `tree-widget.js`.

### Trigger it on a button click

```html
<button id="show-tree">Show Agent Tree</button>
<div id="tree-container"></div>
<script>
  document.getElementById("show-tree").addEventListener("click", function () {
    AgentTreeWidget.render(document.getElementById("tree-container"), treeData);
  });
</script>
```

### Re-rendering with new data

Just call `AgentTreeWidget.render(...)` again with a different `treeData`
object and the same container — it replaces the previous tree.

## Data format

```json
{
  "agent-id": "agent-main",
  "children": [
    { "agent-id": "sub-agent", "children": [
      { "tool-id": "some-tool" }
    ]}
  ]
}
```

- Nodes with `"agent-id"` can have `children` (agents or tools). The
  top-level node is styled as the main/orchestrator agent (amber); nested
  `agent-id` nodes are styled as sub-agents (indigo).
- Nodes with `"tool-id"` are always leaves — no `children` — and styled as
  tools (teal circles).

## Where the data can come from

`AgentTreeWidget.render()` just takes a plain JS object — it doesn't care
where it came from. Common options:

- Hardcoded in the page (see `demo.html`)
- Fetched from your own API: `fetch('/your-endpoint').then(r => r.json()).then(data => AgentTreeWidget.render(container, data))`
- Loaded from a local JSON file via `fetch('./display.json')` — note this
  requires the page to be served over `http://`, not opened as `file://`
  (a browser security restriction on local file fetches, unrelated to this
  widget)

## Styling

The widget injects its own scoped styles (prefixed `.agent-tree-widget`)
into `<head>` on first render, so it won't clash with your page's CSS.
Colors and spacing are defined in `tree-widget.js` if you want to
customize them (search for the `STYLE` string and the `NODE_SPACING_*`
constants).

## Notes

- No Babel/JSX compilation needed — `tree-widget.js` is plain JavaScript
  (`React.createElement` calls), so it's lightweight (~7 KB) and loads
  instantly, unlike the JSX-in-browser approach used elsewhere in this
  project.
- Requires React 18+ (uses `ReactDOM.createRoot`).
