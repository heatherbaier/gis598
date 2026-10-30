-- {{< explorer decision-tree title="Decision tree explorer" height="720" >}}
-- Embeds explorers/<name>.html. The height is only a starting size; the explorer reports its own.
return {
  ["explorer"] = function(args, kwargs, meta)
    local name = pandoc.utils.stringify(args[1])
    local title = pandoc.utils.stringify(kwargs["title"])
    if title == "" then title = name end
    local height = pandoc.utils.stringify(kwargs["height"])
    if height == "" then height = "720" end
    local src = quarto.project.offset .. "/explorers/" .. name .. ".html"
    if quarto.doc.is_format("html") then
      return pandoc.RawBlock("html", string.format(
        '<div class="column-body-outset-right">\n<iframe class="explorer-frame" src="%s" title="%s" scrolling="no" loading="lazy" style="height:%spx"></iframe>\n' ..
        '<p class="explorer-note"><a href="%s" target="_blank" rel="noopener">Open this explorer in its own tab</a></p>\n</div>',
        src, title, height, src))
    end
    return pandoc.Para({ pandoc.Emph({ pandoc.Str("Interactive explorer: " .. title .. ". Available in the online book.") }) })
  end
}
