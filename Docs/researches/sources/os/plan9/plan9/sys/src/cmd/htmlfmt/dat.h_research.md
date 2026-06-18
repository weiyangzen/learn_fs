# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/dat.h

Shared declarations for `htmlfmt`.

- Defines `Bytes`, a growable byte buffer.
- Defines `URLwin`, holding input/output fds, document type, URL, parsed `Item` tree, and `Docinfo`.
- Declares global options `url`, `aflag`, `width`, and `defcharset`.
- Declares HTML loading/rendering, file/memory helpers, charset handling, byte-buffer growth, and URL window cleanup functions.

Depends on Plan 9 `<html.h>` types such as `Item` and `Docinfo`.
