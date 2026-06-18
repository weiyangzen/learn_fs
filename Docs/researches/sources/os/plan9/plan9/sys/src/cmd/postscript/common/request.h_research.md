# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/request.h

Definitions for special PostScript request support.

Key responsibilities:
- Documents `-R` request syntax.
- Defines `MAXREQUEST`.
- Defines `Request` with wanted keyword, page number, and file path.

Usage:
- Included by `request.c` and translators that accept request insertion.
