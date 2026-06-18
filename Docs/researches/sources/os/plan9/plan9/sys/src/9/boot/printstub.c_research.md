# File Research: sources/os/plan9/plan9/sys/src/9/boot/printstub.c

Minimal print-format locking/stub helpers.

Key behavior:
- Defines `_fmtlock()`/`_fmtunlock()` using a static `Lock`.
- Defines `_efgfmt()` returning `-1`.

This supplies small libc formatting hooks for constrained boot linkage.
