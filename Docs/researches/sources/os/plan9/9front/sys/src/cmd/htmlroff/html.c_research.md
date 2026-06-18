# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/html.c

Manages explicit and inline HTML tags emitted by `htmlroff`.

Key points:
- Keeps two tag stacks:
  - `tagstack` for block-like `.html` tags that can be closed by id.
  - `tagset` for inline `.ihtml` tags such as current font spans.
- `closingtag` derives closing tags from an opening HTML snippet and handles self-closing/open-close cases.
- `html` emits a block tag, closes any previous tag with the same id, and tracks auto-closing unless id is `-`.
- `closehtml` closes all remaining block tags at EOF.
- `ihtml` toggles inline tags by id, emits close/reopen sequences to keep nesting valid, and avoids duplicate opens.
- `hideihtml` and `showihtml` temporarily close/reopen inline tags around paragraph breaks or raw tag emission.
- Defines escapes for raw `<`, `>`, `&`, quotes, backticks, and minus sentinels.
- `r_html` implements `.html` and `.ihtml` raw requests, translating literal HTML characters into sentinel runes.
- `htmlinit` registers HTML raw requests/escapes and defines the default `font` macro mapping roff font/size state to HTML spans/tags.

Dependencies and interactions:
- Called by `roff.c` paragraph/output logic and font macros.
- Uses string/register functions from `t8.c`.

Research relevance:
- This is the output correctness layer that keeps generated HTML tags balanced despite roff’s stateful formatting model.
