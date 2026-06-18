# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/config

Configuration defaults for the Plan 9 PostScript package.

Key responsibilities:
- Sets `SYSTEM=plan9`, version, root, binary/library/font paths, Datakit flags, page rounding flag, make command, and makefile name.

Important behavior:
- `POSTBIN` derives from `$ROOT/$objtype/bin/aux`.
- Plan 9 font/prologue directories are `/sys/lib/troff/font` and `/sys/lib/postscript/prologues`.
