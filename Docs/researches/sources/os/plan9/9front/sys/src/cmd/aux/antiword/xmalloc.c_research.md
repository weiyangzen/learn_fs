# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/xmalloc.c

Fail-fast allocation wrapper module.

Key routines:
- `xmalloc()` allocates at least one byte and exits fatally on failure.
- `xcalloc()` allocates zeroed memory, with a 16-bit DOS size guard for non-DJGPP builds.
- `xrealloc()` resizes memory and exits fatally on failure.
- `xstrdup()` duplicates strings without relying on platform `strdup()`.
- `xfree()` frees nullable pointers and always returns `NULL`.

Important behavior:
- Zero-size allocations are normalized to one byte for `xmalloc()` and `xcalloc()`.
- `xfree()` supports the project idiom `ptr = xfree(ptr)`.

Dependencies:
- `werr()` platform error handler and debug macros.

Research relevance:
- Provides consistent allocation semantics throughout the parser, avoiding local null-check handling after allocation.
