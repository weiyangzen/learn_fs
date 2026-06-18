# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/runestrcmp.c

This file compares rune strings.

Key behavior:
- `runestrcmp` lexicographically compares two NUL-terminated rune strings.

Important details:
- Returns negative, zero, or positive difference.
