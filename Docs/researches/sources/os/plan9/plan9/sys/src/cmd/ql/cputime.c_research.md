# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/cputime.c

Small host compatibility wrappers for linker timing and file operations.

Key responsibilities:
- Computes CPU time by summing `times()` user/system counters and dividing by 100.
- Wraps `lseek()` behind Plan 9-style `seek()`.
- Wraps host `creat()` behind Plan 9-style `create()`, accepting only mode `1`.

Dependencies:
- Used by the linker’s verbose timing and output-file creation paths.

Notable risks:
- CPU tick scaling assumes 100 ticks per second.
- `create()` is a narrow compatibility shim and returns `-1` for modes other than `1`.
