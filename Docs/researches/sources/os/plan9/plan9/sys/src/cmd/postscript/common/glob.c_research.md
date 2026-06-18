# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/glob.c

Shared global variable definitions for portable PostScript tools.

Key responsibilities:
- Defines `argc`, `argv`, exit/debug/ignore flags, current line/byte position, program name, temp file, font encoding, bounding-box settings, page dimensions, and input/output encoding modes.

Important behavior:
- Defaults `reading` to UTF encoding and `writing` to `WRITING` from `gen.h`.
