# File Research: sources/os/plan9/9front/sys/src/cmd/qi/float.c

Floating-point instruction support for the `qi` Power simulator.

Key responsibilities:
- Defines opcode tables for groups 59 and 63 floating-point/FPSCR instructions.
- `fpreginit` initializes simulated floating registers, including compiler-known constants.
- Implements `lfs/lfd/stfs/stfd` and indexed/update forms.
- Implements FPSCR moves and bit updates: `mcrfs`, `mffs`, `mtfsb1`, `mtfsb0`, `mtfsf`, `mtfsfi`.
- Implements `fcmp`, single/double arithmetic (`fariths`, `farith`), unary moves/abs/neg (`farith2`), and condition/FPSCR updates.
- Converts between double and raw 64-bit words with `v2fp`/`fp2v`.

Dependencies and coupling:
- Uses memory accessors, `reg.fd[]`, FPSCR constants from `power.h`, `getfsr`, and trace/error globals.
- Connected to `run.c` through `ops59`, `ops63a`, and `ops63b`.

Notable behavior:
- Comments explicitly warn that NaN, infinity, exception, and rounding behavior is approximate.
