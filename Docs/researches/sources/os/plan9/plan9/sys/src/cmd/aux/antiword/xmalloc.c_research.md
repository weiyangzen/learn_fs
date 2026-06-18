# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/xmalloc.c

This file wraps memory allocation with fatal error handling.

Key behavior:
- `xmalloc()`, `xcalloc()`, and `xrealloc()` never return `NULL`; they call `werr(1, ...)` on allocation failure.
- Zero-size `malloc`/`calloc` requests are normalized to one byte/item.
- `xstrdup()` provides a portable string duplicate implementation.
- `xfree()` frees non-null pointers and returns `NULL` for assignment-style cleanup.

Important details:
- 16-bit DOS builds reject allocations larger than segment-addressable memory in `xcalloc()`.
- Most list managers in this group depend on `xfree()` returning `NULL` to reset pointers.

Filesystem relevance:
- None directly; supports robust allocation while parsing file data.
