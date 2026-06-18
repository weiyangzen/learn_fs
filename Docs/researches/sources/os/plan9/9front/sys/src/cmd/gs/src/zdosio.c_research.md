# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdosio.c

Implements MS-DOS direct I/O diagnostic operators.

Key behavior:
- Defines `.inport`, `.inportb`, `.outport`, `.outportb`, `.peek`, and `.poke`.
- Reads/writes hardware I/O ports through DOS runtime functions.
- Reads/writes arbitrary byte memory addresses through integer operands.
- File comment explicitly says this should never be included in a released configuration.

Dependencies:
- Uses `dos_.h` direct port routines and interpreter operand checks.

Research notes:
- This is privileged, unsafe debugging functionality. The memory and port operators bypass normal Ghostscript safety boundaries.
