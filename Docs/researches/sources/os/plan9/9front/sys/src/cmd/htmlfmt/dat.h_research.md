# File Research: sources/os/plan9/9front/sys/src/cmd/htmlfmt/dat.h

Defines shared structures, globals, and prototypes for `htmlfmt`.

Key points:
- Defines `Bytes`, a growable byte buffer.
- Defines `URLwin`, a minimal document/render context with input/output fds, document type, URL, parsed items, and document metadata.
- Declares global options `url`, `aflag`, and `width`.
- Declares HTML loading/rendering, URL window cleanup, allocation/string helpers, error reporting, and buffer growth functions.
- Sets stack and event constants, though this command mostly uses batch rendering.

Dependencies and interactions:
- Uses `Item` and `Docinfo` from Plan 9 `<html.h>`.
- Shared by `html.c`, `main.c`, and `util.c`.

Research relevance:
- This is the small internal interface for the `htmlfmt` command.
