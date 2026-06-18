# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/plan9.h

Purpose: Plan 9 platform include shim for bzip2.

Key points:
- Includes `<u.h>`, `<libc.h>`, and `<ctype.h>`.
- Maps `exit(x)` to `exits((x) ? "whoops" : nil)`.
- Defines `size_t` as `ulong`.

Dependencies and interactions:
- Included via `os.h` when `PLAN9` is defined.

Research notes:
- This is a minimal compatibility layer to let upstream-style C code compile against Plan 9 libc conventions.
