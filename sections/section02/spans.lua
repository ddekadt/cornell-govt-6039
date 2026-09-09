-- map revealjs span/div classes onto LaTeX for the beamer render
function Span(el)
  if el.classes:includes("accent") then
    local out = {pandoc.RawInline("latex", "\\accentspan{")}
    for _, v in ipairs(el.content) do table.insert(out, v) end
    table.insert(out, pandoc.RawInline("latex", "}"))
    return out
  elseif el.classes:includes("muted") then
    local out = {pandoc.RawInline("latex", "\\textcolor{gray}{")}
    for _, v in ipairs(el.content) do table.insert(out, v) end
    table.insert(out, pandoc.RawInline("latex", "}"))
    return out
  end
end
function Div(el)
  if el.classes:includes("big") then
    return {pandoc.RawBlock("latex", "\\begin{center}\\large\\bfseries"),
            pandoc.Div(el.content),
            pandoc.RawBlock("latex", "\\end{center}")}
  elseif el.classes:includes("smaller") then
    return {pandoc.RawBlock("latex", "{\\footnotesize"),
            pandoc.Div(el.content),
            pandoc.RawBlock("latex", "}")}
  elseif el.classes:includes("notes") then
    return {}          -- speaker notes stay out of the printed deck
  end
end
