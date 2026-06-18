# File Research: sources/os/plan9/plan9/sys/src/9/omap/fpiarm.c

Implements ARM floating-point instruction emulation and selected atomic/exclusive instruction emulation.

Key points:
- Emulates the older ARM floating-point instruction set using Plan 9 `fpi` internal double-precision arithmetic; does not fully model ARM-visible FP status/traps.
- Defines register offset mapping from `Ureg` to ARM general registers and PC.
- Maintains FP constants for encoded immediate constants 0, 1, 2, 3, 4, 5, 0.5, and 10.
- Implements binary FP operations add, subtract, reverse subtract, multiply, divide, and reverse divide.
- Implements unary FP operations move, negate, absolute value, and round.
- `fcmp()` sets ARM condition flags from FP comparison, returning unordered as V|C.
- `fpemu()` decodes and emulates LDF/STF, CPRT transfers/comparisons, FP status/control moves, integer/FP conversion, and arithmetic instructions; unsupported/deprecated operations call `unimp()`.
- `condok()` evaluates ARM condition codes against `psr`.
- `casemu()` emulates a compare-and-swap style instruction with interrupt exclusion.
- `ldrex()`, `strex()`, and `clrex()` emulate ARM exclusive load/store state with a simple global validity flag.
- `specialopc[]` recognizes LDREX, STREX, CLREX, and CAS-like opcodes before FP decoding.
- `fpiarm()` initializes per-proc FP emulation state on first use, then loops over consecutive emulatable/special instructions, advancing PC until a non-FP instruction is reached.

Dependencies and interactions:
- Uses `../port/fpi.h` arithmetic/conversion helpers.
- Called by trap/undefined-instruction handling through declarations in `fns.h`.
- Stores state in `up->fpsave`.

Research relevance:
- Compatibility layer for ARM FP instructions and atomic primitives where hardware/compiler support is incomplete.
