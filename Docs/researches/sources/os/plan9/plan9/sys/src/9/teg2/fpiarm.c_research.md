# File Research: sources/os/plan9/plan9/sys/src/9/teg2/fpiarm.c

Implements software emulation for old ARM FPA/FPA-like floating point instructions, layered on Plan 9’s portable `../port/fpi.h` internal floating-point routines.

Key behavior:
- Decodes ARM conditional execution, FPA load/store, register transfer, compare, unary, and binary arithmetic opcodes.
- Maintains emulated FP state in `up->fpsave`, switching process FP state to `FPemu` on first use.
- Supports constants and 8 legacy FPA registers under `ARM7500`.
- Advances `ureg->pc` over each emulated instruction and stops when the instruction stream is no longer an FPA opcode.

Important functions:
- `fpiarm(Ureg*)`: top-level emulator entry used from undefined-instruction trap handling.
- `fpemu(...)`: decodes and executes one FP opcode.
- `fcmp`, `fld`, `fst`, arithmetic helpers: implement individual operations using `fpi*` helpers.

Notes:
- Does not fully model ARM floating-point trap status or properties beyond what the Plan 9/Inferno environment needs.
- Raises errors for unsupported opcodes and for mixing emulated FPA state with VFP mode.
