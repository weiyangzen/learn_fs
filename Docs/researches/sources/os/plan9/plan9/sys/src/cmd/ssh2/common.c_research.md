# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/common.c

Small SSH2 utility module.

Key responsibilities:
- `freeptr`: frees a pointed-to pointer and sets it to nil.
- `readfile`: reads up to `size-1` bytes from a file into a NUL-terminated buffer.

Risks/quirks:
- `freeptr` accepts `void **` but casts to `char **`; intended for pointer cleanup rather than typed ownership.
- `readfile` returns `-1` on open failure and leaves caller's buffer unchanged in that case.
