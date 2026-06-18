# File Research: sources/os/plan9/plan9/sys/src/9/port/print.c

Small formatting support file.

Functions:
- `_fmtlock`: acquires a static formatting lock.
- `_fmtunlock`: releases the formatting lock.
- `_efgfmt`: placeholder formatter returning `-1`.

Role:
- Provides lock hooks for the Plan 9 formatting library in kernel context.
- `_efgfmt` disables or stubs floating-point format handling in this port context.
