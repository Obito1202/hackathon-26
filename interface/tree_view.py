import json
from typing import Any

_STYLE = """
:root {
  --bg: #0f172a;
  --text: #e2e8f0;
  --muted: #94a3b8;
  --edge: #475569;

  --root-a: #f59e0b;
  --root-b: #d97706;
  --agent-a: #6366f1;
  --agent-b: #4338ca;
  --tool-a: #10b981;
  --tool-b: #047857;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif;
  background: radial-gradient(circle at 20% 0%, #1e293b 0%, var(--bg) 60%);
  color: var(--text);
  min-height: 100vh;
}

header { padding: 24px 32px 8px; }
header h1 { margin: 0 0 4px; font-size: 22px; font-weight: 700; letter-spacing: -0.02em; }
header p { margin: 0; color: var(--muted); font-size: 13px; }

.legend { display: flex; gap: 20px; padding: 12px 32px 20px; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--muted); }
.swatch { width: 14px; height: 14px; border-radius: 4px; display: inline-block; }
.swatch.root { background: linear-gradient(135deg, var(--root-a), var(--root-b)); }
.swatch.agent { background: linear-gradient(135deg, var(--agent-a), var(--agent-b)); }
.swatch.tool { background: linear-gradient(135deg, var(--tool-a), var(--tool-b)); border-radius: 50%; }

#canvas-wrap { overflow: auto; padding: 0 16px 48px; }
.tree-canvas { position: relative; margin: 0 auto; }
.edge-svg { position: absolute; top: 0; left: 0; pointer-events: none; }

.node {
  position: absolute;
  transform: translate(-50%, -50%);
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 10px 14px;
  color: white;
  font-size: 12.5px;
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(0,0,0,0.35);
  border: 1px solid rgba(255,255,255,0.15);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  cursor: default;
  line-height: 1.3;
  white-space: nowrap;
}
.node:hover { transform: translate(-50%, -50%) scale(1.08); box-shadow: 0 6px 20px rgba(0,0,0,0.5); z-index: 5; }
.node.root { background: linear-gradient(135deg, var(--root-a), var(--root-b)); border-radius: 14px; min-width: 150px; height: 52px; font-size: 14px; }
.node.agent { background: linear-gradient(135deg, var(--agent-a), var(--agent-b)); border-radius: 12px; min-width: 130px; height: 46px; }
.node.tool { background: linear-gradient(135deg, var(--tool-a), var(--tool-b)); border-radius: 50%; width: 96px; height: 96px; white-space: normal; }
.node .tag {
  position: absolute; top: -9px; font-size: 9px; font-weight: 700; letter-spacing: 0.05em;
  text-transform: uppercase; background: rgba(15, 23, 42, 0.9); padding: 1px 6px; border-radius: 6px; color: var(--muted);
}
"""

_APP_JS = """
const { useMemo } = React;

const NODE_SPACING_X = 170;
const NODE_SPACING_Y = 150;
const PADDING = 90;

function normalize(raw, depth) {
  const isAgent = Object.prototype.hasOwnProperty.call(raw, "agent-id");
  const id = isAgent ? raw["agent-id"] : raw["tool-id"];
  const type = isAgent ? (depth === 0 ? "root" : "agent") : "tool";
  const children = (raw.children || []).map((c) => normalize(c, depth + 1));
  return { id, type, depth, children };
}

function assignX(node, cursor) {
  if (!node.children.length) {
    node.x = cursor.value;
    cursor.value += 1;
    return node.x;
  }
  const xs = node.children.map((c) => assignX(c, cursor));
  node.x = (Math.min(...xs) + Math.max(...xs)) / 2;
  return node.x;
}

function flatten(node, acc) {
  acc.nodes.push(node);
  node.children.forEach((c) => {
    acc.edges.push([node, c]);
    flatten(c, acc);
  });
  return acc;
}

function prettyLabel(id) {
  return String(id).replace(/^(agent|tool)-/, "").split("-").join(" ");
}

function Edge({ from, to }) {
  const x1 = from.x * NODE_SPACING_X + PADDING;
  const y1 = from.depth * NODE_SPACING_Y + PADDING;
  const x2 = to.x * NODE_SPACING_X + PADDING;
  const y2 = to.depth * NODE_SPACING_Y + PADDING;
  const midY = (y1 + y2) / 2;
  const path = `M ${x1} ${y1} C ${x1} ${midY}, ${x2} ${midY}, ${x2} ${y2}`;
  return <path d={path} stroke="var(--edge)" strokeWidth="1.6" fill="none" />;
}

function Node({ node }) {
  const left = node.x * NODE_SPACING_X + PADDING;
  const top = node.depth * NODE_SPACING_Y + PADDING;
  const tagText = node.type === "root" ? "orchestrator" : node.type;
  return (
    <div className={`node ${node.type}`} style={{ left, top }}>
      <span className="tag">{tagText}</span>
      {prettyLabel(node.id)}
    </div>
  );
}

function App() {
  const { nodes, edges, width, height } = useMemo(() => {
    const tree = normalize(window.__TREE_DATA__, 0);
    assignX(tree, { value: 0 });
    const flat = flatten(tree, { nodes: [], edges: [] });
    const maxX = Math.max(...flat.nodes.map((n) => n.x));
    const maxDepth = Math.max(...flat.nodes.map((n) => n.depth));
    return {
      nodes: flat.nodes,
      edges: flat.edges,
      width: maxX * NODE_SPACING_X + PADDING * 2,
      height: maxDepth * NODE_SPACING_Y + PADDING * 2,
    };
  }, []);

  return (
    <React.Fragment>
      <header>
        <h1>Agent &amp; Tool Topology</h1>
        <p>Rendered from the JSON posted to /visualize.</p>
      </header>
      <div className="legend">
        <div className="legend-item"><span className="swatch root"></span>Main / orchestrator agent</div>
        <div className="legend-item"><span className="swatch agent"></span>Sub-agent</div>
        <div className="legend-item"><span className="swatch tool"></span>Tool (leaf)</div>
      </div>
      <div id="canvas-wrap">
        <div className="tree-canvas" style={{ width, height }}>
          <svg className="edge-svg" width={width} height={height}>
            {edges.map(([from, to], i) => (
              <Edge key={i} from={from} to={to} />
            ))}
          </svg>
          {nodes.map((n) => (
            <Node key={n.id} node={n} />
          ))}
        </div>
      </div>
    </React.Fragment>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
"""

_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Agent Tree Visualizer</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>{style}</style>
</head>
<body>
<div id="root"></div>

<script>window.__TREE_DATA__ = {data};</script>

<script src="{vendor_prefix}/react.production.min.js"></script>
<script src="{vendor_prefix}/react-dom.production.min.js"></script>
<script src="{vendor_prefix}/babel.min.js"></script>

<script type="text/plain" id="app-src">{app_js}</script>
<script>
  var src = document.getElementById("app-src").textContent;
  var compiled = Babel.transform(src, {{
    presets: [["react", {{ runtime: "classic" }}]],
  }}).code;
  new Function(compiled)();
</script>
</body>
</html>
"""


def render_tree_html(data: Any, vendor_prefix: str = "/vendor") -> str:
    safe_json = json.dumps(data).replace("</", "<\\/")
    return _PAGE_TEMPLATE.format(
        style=_STYLE,
        data=safe_json,
        vendor_prefix=vendor_prefix,
        app_js=_APP_JS,
    )
