# File Research: sources/os/plan9/9front/sys/src/cmd/htmlfmt/html.c

Renders Plan 9 `<html.h>` parsed document items to wrapped plain text.

Key points:
- `loadhtml` reads all input into a `Bytes` buffer, builds a `URLwin`, calls `rendertext`, and frees parsed document state.
- `rendertext` converts the current URL to runes and calls `parsehtml` to obtain item lists and document metadata.
- Word wrapping uses globals `inword`, `col`, and `wordi`; `emitword` inserts spaces unless the preceding output is whitespace or the word begins with closing punctuation.
- `renderrunes` collapses spaces, preserves blank-line limits, and wraps at `width`.
- URL handling:
  - `baseurl` extracts a scheme/authority/path base using a regexp.
  - `fullurl` resolves relative hrefs against the document URL.
- `render` walks item lists:
  - text is wrapped or emitted as a word depending on `IFwrap`
  - rules render as separator lines
  - images/forms are shown only with `-a`
  - tables render by recursively rendering each cell
  - floats recurse into contained items
  - spacers emit spaces
  - anchors render as numeric references or full URLs depending on `-a`
- `rerender` emits title text, rendered body, and optional reference list.

Dependencies and interactions:
- Uses Plan 9 `<html.h>` structures (`Item`, `Itext`, `Iimage`, `Itable`, `Anchor`, etc.).
- Uses utility functions from `util.c`.

Research relevance:
- This is a text extractor/formatter built around the Plan 9 HTML parser, complementary to the hand-rolled `html2ms.c`.
