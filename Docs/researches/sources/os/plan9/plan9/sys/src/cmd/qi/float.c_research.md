# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/float.c

Floating-point instruction emulation for the PowerPC interpreter.

Key responsibilities:
- Defines opcode tables for primary opcodes 59 and 63 floating-point operations.
- Initializes floating registers, including compiler-reserved constants.
- Converts between raw 64-bit memory values and host doubles.
- Emulates floating loads/stores, indexed/update variants, FPSCR moves/field updates, comparisons, unary operations, arithmetic, fused multiply-add/subtract families, and result condition bits.
- Tracks a subset of FPSCR exception state using host floating status.

Dependencies:
- Uses `power.h` register state, memory accessors, decode macros, FPSCR constants, and Plan 9 floating conversion helpers.

Notable risks:
- Comments explicitly warn that NaN, infinity, rounding, and exception behavior are approximate.
- Single-precision stores rely on host conversion through C `float`.
- Some optional operations are routed to `unimp`.
