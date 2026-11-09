-- Numbers the section headings inside a chapter from the number at the start of its title.
-- A chapter titled "3.2 Decision trees" gets sections 3.2.1, 3.2.2, and so on, with
-- subsections 3.2.1.1 and so on. A title with no leading number (Preface, References)
-- is left alone. Quarto's own numbering is turned off in _quarto.yml.
local prefix = nil
local counters = { 0, 0, 0 }

return {
  {
    Meta = function(meta)
      local title = meta.title and pandoc.utils.stringify(meta.title) or ""
      prefix = title:match("^(%d+[%.%d]*)%s")
      return nil
    end,
  },
  {
    Header = function(h)
      if not prefix or h.level < 2 or h.level > 4 or h.classes:includes("unnumbered") then
        return nil
      end
      local depth = h.level - 1
      counters[depth] = counters[depth] + 1
      for i = depth + 1, #counters do counters[i] = 0 end
      local number = prefix
      for i = 1, depth do number = number .. "." .. counters[i] end
      h.content:insert(1, pandoc.Space())
      h.content:insert(1, pandoc.Span(number, pandoc.Attr("", { "header-section-number" })))
      return h
    end,
  },
}
