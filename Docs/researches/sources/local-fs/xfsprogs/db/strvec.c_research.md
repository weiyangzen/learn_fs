# File Research: sources/local-fs/xfsprogs/db/strvec.c

Implements NULL-terminated string vector helpers.

Key responsibilities:
- Allocates new vectors with space for a trailing NULL.
- Adds duplicated strings, copies vectors, frees vectors, and prints vector contents.
- Uses xfsprogs allocation wrappers and `dbprintf`.

Important behavior:
- `add_strvec` reallocates the vector to append one duplicated string.
- `copy_strvec` duplicates every source entry.
- `print_strvec` emits entries without separators.

Dependencies:
- Uses `xmalloc`, `xrealloc`, `xstrdup`, `xfree`, and `dbprintf`.

Notable risks:
- Functions assume input vectors are non-NULL and properly NULL-terminated.
