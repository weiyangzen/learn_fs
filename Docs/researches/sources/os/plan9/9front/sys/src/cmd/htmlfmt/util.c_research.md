# File Research: sources/os/plan9/9front/sys/src/cmd/htmlfmt/util.c

Provides allocation, string, error, and buffer utilities for `htmlfmt`.

Key points:
- `emalloc` and `erealloc` fatal-exit on allocation failure.
- `estrdup`, `estrstrdup`, `eappend`, and `egrow` build heap strings, with `eappend` freeing the previous base string.
- `error` formats an error to fd 2 and exits; it prefixes messages with `Mail:`, likely inherited from related mail/web tooling.
- `growbytes` expands a `Bytes` buffer in 8000-byte increments, appends data, and NUL-terminates.

Dependencies and interactions:
- Shared by `html.c` and `main.c`.
- Uses Plan 9 `Fmt` for error formatting.

Research relevance:
- This is support code for robust batch rendering and URL/string assembly.
