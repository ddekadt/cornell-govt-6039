-- Quarto filter for Section 9.
--   ::: {.algo title="..."}   algorithm / model box (blue rule), in every version
--   ::: sol                   worked answer; ::: {.sol label="Note"} for a note
-- HTML: answers become closed toggles, plus a "show all" button.
-- PDF: answers are printed in red with a rule down the left margin.
-- With `solutions: false` in the metadata the answer blocks are dropped.

local show = true
local found = false

local css = [[
<style>
details.sol { margin: 0.5rem 0 1.5rem 0; }
details.sol > summary {
  display: inline-flex; align-items: center; gap: 0.45em;
  cursor: pointer; list-style: none; user-select: none;
  font-size: 0.8rem; font-weight: 600; letter-spacing: 0.03em; text-transform: uppercase;
  color: #b3261e; background: #fdf3f2; border: 1px solid #ecc4c0;
  border-radius: 999px; padding: 0.2rem 0.85rem;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
details.sol > summary::-webkit-details-marker { display: none; }
details.sol > summary::before {
  content: ""; width: 0; height: 0;
  border-left: 0.42em solid currentColor; border-top: 0.3em solid transparent; border-bottom: 0.3em solid transparent;
  transition: transform 0.15s;
}
details.sol > summary:hover { border-color: #b3261e; }
details.sol[open] > summary { background: #b3261e; color: #fff; border-color: #b3261e; }
details.sol[open] > summary::before { transform: rotate(90deg); }
details.sol > .sol-body {
  margin-top: 0.65rem; padding: 0.8rem 1.1rem;
  border-left: 3px solid #b3261e; border-radius: 0 6px 6px 0;
  background: #fdf7f6; color: #3b1512;
}
details.sol > .sol-body > :last-child { margin-bottom: 0; }
.algo {
  margin: 1rem 0 1.5rem 0; padding: 0.9rem 1.2rem;
  background: #f4f7fc; border-left: 3px solid #2a78d6; border-radius: 0 6px 6px 0;
}
.algo > .algo-title {
  font-size: 0.78rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;
  color: #2a78d6; margin-bottom: 0.55rem;
}
.algo > :last-child { margin-bottom: 0; }
#sol-toggle-all {
  position: fixed; right: 1.2rem; bottom: 1.2rem; z-index: 1000;
  font-size: 0.78rem; font-weight: 600; letter-spacing: 0.03em; text-transform: uppercase;
  color: #b3261e; background: #fff; border: 1px solid #ecc4c0; border-radius: 999px;
  padding: 0.4rem 0.95rem; box-shadow: 0 1px 4px rgba(0,0,0,0.12); cursor: pointer;
}
#sol-toggle-all:hover { border-color: #b3261e; }
@media print { #sol-toggle-all { display: none; } }
</style>
]]

local js = [[
<button id="sol-toggle-all" type="button">Show all answers</button>
<script>
(function () {
  var b = document.getElementById("sol-toggle-all");
  b.addEventListener("click", function () {
    var all = document.querySelectorAll("details.sol");
    var open = b.getAttribute("data-open") !== "1";
    all.forEach(function (d) { d.open = open; });
    b.setAttribute("data-open", open ? "1" : "0");
    b.textContent = open ? "Hide all answers" : "Show all answers";
  });
})();
</script>
]]

local function read_meta(meta)
  if meta.solutions ~= nil then
    show = (meta.solutions == true) or (pandoc.utils.stringify(meta.solutions) == "true")
  end
end

local function algo_div(el)
  local title = el.attributes["title"] or ""
  if quarto.doc.is_format("pdf") then
    local out = pandoc.List({pandoc.RawBlock("latex", "\\begin{algobox}{" .. title .. "}")})
    out:extend(el.content)
    out:insert(pandoc.RawBlock("latex", "\\end{algobox}"))
    return out
  end
  if quarto.doc.is_format("html") then
    local out = pandoc.List({pandoc.RawBlock("html",
      '<div class="algo"><div class="algo-title">' .. title .. '</div>')})
    out:extend(el.content)
    out:insert(pandoc.RawBlock("html", "</div>"))
    return out
  end
  return el.content
end

local function sol_div(el)
  if el.classes:includes("algo") then return algo_div(el) end
  if not el.classes:includes("sol") then return nil end
  if not show then return {} end
  found = true
  local label = el.attributes["label"] or "Answer"

  if quarto.doc.is_format("pdf") then
    local content = el.content
    if #content > 0 and content[1].t == "Para" then
      content[1].content:insert(1, pandoc.Space())
      content[1].content:insert(1, pandoc.Strong({pandoc.Str(label .. ".")}))
    end
    local out = pandoc.List({pandoc.RawBlock("latex", "\\begin{solbox}")})
    out:extend(content)
    out:insert(pandoc.RawBlock("latex", "\\end{solbox}"))
    return out
  end

  if quarto.doc.is_format("html") then
    local out = pandoc.List({pandoc.RawBlock("html",
      '<details class="sol"><summary>' .. label .. '</summary><div class="sol-body">')})
    out:extend(el.content)
    out:insert(pandoc.RawBlock("html", "</div></details>"))
    return out
  end

  return el.content
end

local function add_assets(doc)
  if quarto.doc.is_format("html") then
    doc.blocks:insert(1, pandoc.RawBlock("html", css))
    if found then doc.blocks:insert(pandoc.RawBlock("html", js)) end
  end
  return doc
end

return {{Meta = read_meta}, {Div = sol_div}, {Pandoc = add_assets}}
