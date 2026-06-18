# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/html.c

HTML tag emission and inline HTML state management for `htmlroff`.

- Maintains a stack of block HTML tags and a set/stack of active inline HTML tags.
- `html()` emits block HTML, closes any previous tag with the same id, computes closing tags, and stacks them unless id `-` means immediate close.
- `closehtml()` closes all remaining block tags.
- `ihtml()` manages inline tag changes, closing/reopening nested inline tags as needed.
- `hideihtml()` and `showihtml()` temporarily suppress/reemit inline tags around breaks and block transitions.
- `r_html()` implements `.html` and `.ihtml` raw requests, reading a line in HTML mode and converting raw `<`, `>`, `&`, and spaces to internal sentinels.
- `htmlinit()` registers raw requests, escape handlers, and default font-to-HTML mapping macros.

Notable concerns: `closingtag()` is a heuristic parser for tag strings; it handles ordinary tags and self-closing/closing tags but is not a general HTML parser.
