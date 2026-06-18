# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zdosio.c

Implements MS-DOS direct I/O and raw memory operators.

Operators:
- `.inport`
- `.inportb`
- `.outport`
- `.outportb`
- `.peek`
- `.poke`

The file explicitly warns it should never be included in a released configuration.

The port operators call DOS `inport`, `inportb`, `outport`, and `outportb`. The memory operators cast integer operands to byte pointers for raw reads/writes.

Risk is intentionally high: these operators expose direct hardware port and memory access to PostScript code.

Registered in `zdosio_op_defs`.
