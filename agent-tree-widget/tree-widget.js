(function () {
  if (typeof React === "undefined" || typeof ReactDOM === "undefined") {
    throw new Error("tree-widget.js requires React and ReactDOM to be loaded first");
  }

  var STYLE = "\
:root {\
  --bg: #0f172a; --text: #e2e8f0; --muted: #94a3b8; --edge: #475569;\
  --root-a: #f59e0b; --root-b: #d97706;\
  --agent-a: #6366f1; --agent-b: #4338ca;\
  --tool-a: #10b981; --tool-b: #047857;\
}\
.agent-tree-widget * { box-sizing: border-box; }\
.agent-tree-widget {\
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, sans-serif;\
  background: radial-gradient(circle at 20% 0%, #1e293b 0%, var(--bg) 60%);\
  color: var(--text);\
  border-radius: 12px;\
  overflow: hidden;\
}\
.agent-tree-widget header { padding: 24px 32px 8px; }\
.agent-tree-widget header h1 { margin: 0 0 4px; font-size: 22px; font-weight: 700; letter-spacing: -0.02em; }\
.agent-tree-widget header p { margin: 0; color: var(--muted); font-size: 13px; }\
.agent-tree-widget .legend { display: flex; gap: 20px; padding: 12px 32px 20px; flex-wrap: wrap; }\
.agent-tree-widget .legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--muted); }\
.agent-tree-widget .swatch { width: 14px; height: 14px; border-radius: 4px; display: inline-block; }\
.agent-tree-widget .swatch.root { background: linear-gradient(135deg, var(--root-a), var(--root-b)); }\
.agent-tree-widget .swatch.agent { background: linear-gradient(135deg, var(--agent-a), var(--agent-b)); }\
.agent-tree-widget .swatch.tool { background: linear-gradient(135deg, var(--tool-a), var(--tool-b)); border-radius: 50%; }\
.agent-tree-widget .canvas-wrap { overflow: auto; padding: 0 16px 48px; }\
.agent-tree-widget .tree-canvas { position: relative; margin: 0 auto; }\
.agent-tree-widget .edge-svg { position: absolute; top: 0; left: 0; pointer-events: none; }\
.agent-tree-widget .node {\
  position: absolute; transform: translate(-50%, -50%);\
  display: flex; align-items: center; justify-content: center; text-align: center;\
  padding: 10px 14px; color: white; font-size: 12.5px; font-weight: 600;\
  box-shadow: 0 4px 14px rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.15);\
  transition: transform 0.15s ease, box-shadow 0.15s ease; cursor: default;\
  line-height: 1.3; white-space: nowrap;\
}\
.agent-tree-widget .node:hover { transform: translate(-50%, -50%) scale(1.08); box-shadow: 0 6px 20px rgba(0,0,0,0.5); z-index: 5; }\
.agent-tree-widget .node.root { background: linear-gradient(135deg, var(--root-a), var(--root-b)); border-radius: 14px; min-width: 150px; height: 52px; font-size: 14px; }\
.agent-tree-widget .node.agent { background: linear-gradient(135deg, var(--agent-a), var(--agent-b)); border-radius: 12px; min-width: 130px; height: 46px; }\
.agent-tree-widget .node.tool { background: linear-gradient(135deg, var(--tool-a), var(--tool-b)); border-radius: 50%; width: 96px; height: 96px; white-space: normal; }\
.agent-tree-widget .node .tag {\
  position: absolute; top: -9px; font-size: 9px; font-weight: 700; letter-spacing: 0.05em;\
  text-transform: uppercase; background: rgba(15, 23, 42, 0.9); padding: 1px 6px; border-radius: 6px; color: var(--muted);\
}\
";

  function injectStyleOnce() {
    if (document.getElementById("agent-tree-widget-style")) return;
    var styleEl = document.createElement("style");
    styleEl.id = "agent-tree-widget-style";
    styleEl.textContent = STYLE;
    document.head.appendChild(styleEl);
  }

  var NODE_SPACING_X = 170;
  var NODE_SPACING_Y = 150;
  var PADDING = 90;

  function normalize(raw, depth) {
    var isAgent = Object.prototype.hasOwnProperty.call(raw, "agent-id");
    var id = isAgent ? raw["agent-id"] : raw["tool-id"];
    var type = isAgent ? (depth === 0 ? "root" : "agent") : "tool";
    var children = (raw.children || []).map(function (c) { return normalize(c, depth + 1); });
    return { id: id, type: type, depth: depth, children: children };
  }

  function assignX(node, cursor) {
    if (!node.children.length) {
      node.x = cursor.value;
      cursor.value += 1;
      return node.x;
    }
    var xs = node.children.map(function (c) { return assignX(c, cursor); });
    node.x = (Math.min.apply(null, xs) + Math.max.apply(null, xs)) / 2;
    return node.x;
  }

  function flatten(node, acc) {
    acc.nodes.push(node);
    node.children.forEach(function (c) {
      acc.edges.push([node, c]);
      flatten(c, acc);
    });
    return acc;
  }

  function prettyLabel(id) {
    return String(id).replace(/^(agent|tool)-/, "").split("-").join(" ");
  }

  var h = React.createElement;

  function Edge(props) {
    var from = props.from, to = props.to;
    var x1 = from.x * NODE_SPACING_X + PADDING;
    var y1 = from.depth * NODE_SPACING_Y + PADDING;
    var x2 = to.x * NODE_SPACING_X + PADDING;
    var y2 = to.depth * NODE_SPACING_Y + PADDING;
    var midY = (y1 + y2) / 2;
    var path = "M " + x1 + " " + y1 + " C " + x1 + " " + midY + ", " + x2 + " " + midY + ", " + x2 + " " + y2;
    return h("path", { d: path, stroke: "var(--edge)", strokeWidth: "1.6", fill: "none" });
  }

  function Node(props) {
    var node = props.node;
    var left = node.x * NODE_SPACING_X + PADDING;
    var top = node.depth * NODE_SPACING_Y + PADDING;
    var tagText = node.type === "root" ? "orchestrator" : node.type;
    return h(
      "div",
      { className: "node " + node.type, style: { left: left, top: top } },
      h("span", { className: "tag" }, tagText),
      prettyLabel(node.id)
    );
  }

  function App(props) {
    var data = props.data;
    var layout = React.useMemo(function () {
      var tree = normalize(data, 0);
      assignX(tree, { value: 0 });
      var flat = flatten(tree, { nodes: [], edges: [] });
      var maxX = Math.max.apply(null, flat.nodes.map(function (n) { return n.x; }));
      var maxDepth = Math.max.apply(null, flat.nodes.map(function (n) { return n.depth; }));
      return {
        nodes: flat.nodes,
        edges: flat.edges,
        width: maxX * NODE_SPACING_X + PADDING * 2,
        height: maxDepth * NODE_SPACING_Y + PADDING * 2,
      };
    }, [data]);

    return h(
      "div",
      { className: "agent-tree-widget" },
      h(
        "header",
        null,
        h("h1", null, "Agent & Tool Topology"),
        h("p", null, "Rendered client-side \u2014 no backend required.")
      ),
      h(
        "div",
        { className: "legend" },
        h("div", { className: "legend-item" }, h("span", { className: "swatch root" }), "Main / orchestrator agent"),
        h("div", { className: "legend-item" }, h("span", { className: "swatch agent" }), "Sub-agent"),
        h("div", { className: "legend-item" }, h("span", { className: "swatch tool" }), "Tool (leaf)")
      ),
      h(
        "div",
        { className: "canvas-wrap" },
        h(
          "div",
          { className: "tree-canvas", style: { width: layout.width, height: layout.height } },
          h(
            "svg",
            { className: "edge-svg", width: layout.width, height: layout.height },
            layout.edges.map(function (pair, i) {
              return h(Edge, { key: i, from: pair[0], to: pair[1] });
            })
          ),
          layout.nodes.map(function (n) {
            return h(Node, { key: n.id, node: n });
          })
        )
      )
    );
  }

  window.AgentTreeWidget = {
    render: function (container, data) {
      injectStyleOnce();
      var root = ReactDOM.createRoot(container);
      root.render(h(App, { data: data }));
      return root;
    },
  };
})();
