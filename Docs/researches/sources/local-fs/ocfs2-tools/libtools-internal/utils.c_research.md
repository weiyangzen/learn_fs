# File Research: sources/local-fs/ocfs2-tools/libtools-internal/utils.c

Provides small string trimming helpers.

Functions:
- `tools_strchomp(char *str)`: removes trailing whitespace in place.
- `tools_strchug(char *str)`: removes leading whitespace in place by `memmove()`.

Dependencies:
- Standard C string and ctype APIs.
- `tools-internal/utils.h`.

Research notes:
- Both functions return the original buffer pointer.
- The file includes a `DEBUG_EXE` self-test for trimming behavior.
