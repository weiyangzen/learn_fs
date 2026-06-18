# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdebug.h

Ghostscript debugging/tracing macro header.

Key points:
- Declares global debug flag array `gs_debug[128]` and `gs_debug_c`.
- Uppercase debug flags also enable corresponding lowercase flags.
- Defines `gs_log_errors` as `gs_debug['#']`.
- Declares `gs_debug_out` and redirects `dstderr`/`estderr` to it when compiled with `DEBUG`.
- Provides `if_debug0` through `if_debug12` macros that emit debug output only when `DEBUG` is compiled in and the flag is set.
- When `DEBUG` is absent, debug macros compile to `DO_NOTHING`.
- Declares debug dump helpers for bytes, bitmaps, strings, and hex strings.

Dependencies and interactions:
- Used throughout Ghostscript for selective runtime tracing.

OS/filesystem relevance:
- Debug output destination may be a file stream, but this header has no file-opening logic.
