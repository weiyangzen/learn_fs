# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/utfecpy.c

This file copies UTF-8 strings into a bounded buffer without cutting a rune.

Key behavior:
- `utfecpy` copies from source into `[to, e)` and backs off to a valid UTF boundary before NUL-terminating.

Important details:
- Used for safe error-string copying.
