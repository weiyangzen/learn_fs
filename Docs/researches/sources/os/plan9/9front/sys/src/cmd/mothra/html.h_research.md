# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/html.h

Defines Mothra’s HTML parser limits, token/tag model, parser state, and form integration interface.

Key behavior:
- Defines limits for stack depth, input buffer, lookahead, token length, and attributes.
- Defines `Pair`, `Entity`, `Tag`, `Stack`, `Hglob`, and incomplete `Form`/`Field`.
- `Stack` stores current tag formatting state including font, size, margins, image/link/name fields, script/pre flags, and image dimensions.
- `Hglob` stores parser input buffers, token/attribute buffers, parse stack, output state, current form, and destination page.
- Enumerates token types, special input sentinels, font/size constants, length direction, and all recognized HTML tag ids.
- Declares `tag[]`, form hooks, attribute helpers, and `pl_htmloutput`.

Important dependencies: Mothra `Www` type, form code, HTML parser implementation elsewhere.

Notable risks:
- Static token/attribute buffers impose hard limits.
- Tag enum order must match `html.syntax.c` table.
