# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vfprint.c

This file formats a `va_list` to an fd.

Key behavior:
- `vfprint` initializes an fd-backed `Fmt`, dispatches formatting, and flushes.

Important details:
- Shared backend for `print` and `fprint`.
