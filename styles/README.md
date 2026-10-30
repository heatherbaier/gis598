# Book styling

`light.scss` and `dark.scss` set the colors and fonts for each theme (the same purple and system font as the explorers). `book.scss` holds the shared rules. All three are listed under `theme:` in `_quarto.yml`.

## Colored blocks

Wrap text in one of these to get a colored box with a small label:

```
::: {.scenario}
A short setup that puts the reader in a situation.
:::

::: {.keyidea}
The one idea from this section to remember.
:::

::: {.definition}
A term and what it means.
:::

::: {.example}
A worked example.
:::
```

## Cards

A bullet list wrapped in `.variables` becomes a grid of cards. Start each bullet with a bold title and write the rest as a full sentence.

```
::: {.variables}
- **Slope (°)** Steep parcels shed water downhill.
- **Drainage class** How well the soil drains.
:::
```

The built-in callouts (`callout-note`, `callout-tip`, `callout-warning`) pick up the same palette automatically.
