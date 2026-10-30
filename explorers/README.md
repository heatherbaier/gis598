# Interactive explorers

Each file in this folder is a self-contained HTML page (its own CSS and JavaScript) that a chapter embeds.

## Embed one in a chapter

```
{{< explorer decision-tree title="Decision tree explorer" height="760" >}}
```

The name is the file name without `.html`. `height` is only a starting size, because the explorer reports its own height once it loads. The shortcode lives in `shortcodes/explorer.lua`, and the script that sizes the frame and passes on the light/dark setting is `includes/explorer-embed.html`.

## Rules for an explorer file

- No site navigation or page header. The book supplies those, and the chapter text supplies the intro.
- Define colors as CSS variables on `:root`, with a dark set under `:root[data-theme="dark"]` and under `@media (prefers-color-scheme: dark)` guarded by `:root:not([data-theme="light"])`.
- Don't size the body to the viewport (no `100vh`), or the frame height can't follow the content.
- Include the small message script at the end of `decision-tree.html`, which sends the page height to the book and receives the theme.
- There is nothing else to register. The `resources` entry in `_quarto.yml` copies everything matching `explorers/*.html`.
