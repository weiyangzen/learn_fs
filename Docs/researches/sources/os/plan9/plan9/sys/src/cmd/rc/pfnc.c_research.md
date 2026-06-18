# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/pfnc.c

Debug printer for rc interpreter execution cycles.

Contents:
- Static `fname[]` maps `X*` opcode function pointers to names.
- `pfnc()` prints current pid, code vector pointer, pc, opcode name or raw pointer, and current argv stack contents.

Used when rc flag `-r` is set in the main dispatch loop.

Risk/notes:
- Function pointer matching requires the exact opcode symbols compiled into the same binary.
