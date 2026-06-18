# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtlock.c

This file defines formatting registry lock hooks.

Key behavior:
- `__fmtlock` and `__fmtunlock` are empty.

Important details:
- The hosted drawterm formatting registry is effectively unlocked here.
