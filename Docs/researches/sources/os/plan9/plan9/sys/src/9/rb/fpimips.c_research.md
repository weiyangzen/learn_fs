# File Research: sources/os/plan9/plan9/sys/src/9/rb/fpimips.c

MIPS COP1 floating-point emulator for a MIPS32r2/24K Plan 9 port without usable hardware FP.

Key responsibilities:
- Keeps raw 32-bit FP register words in `FPsave` and converts to/from Plan 9 internal FP only when needed.
- Decodes COP1 instructions, FP loads/stores, CPU/FP register moves, control-register moves, arithmetic, conversion, comparison, and FP branches.
- Emulates single/double/word/vlong conversions and basic arithmetic using common `fpi` routines.
- Handles MIPS FP register-pair endian ordering for double/vlong transfers.
- Implements FP branch delay-slot behavior, including emulating FP delay slots or executing non-FP delay slots in user mode with watchpoint-assisted return.
- Provides `fpwatch` to complete delayed branch execution after a watchpoint trap.
- Implements branch classification and branch target calculation for integer and FP branches.
- Initializes emulated FP state and Plan 9 constants F24=0.0, F26=0.5, F28=1.0, F30=2.0.
- Exposes `reg()` for fault code and optional debug output through `fpemuprint`.

Important behavior:
- Fakes `MOVW FCR0,R1` as `0x500` to advertise R4000-style LL/SC capability.
- Can emulate runs of consecutive FP instructions in one trap.
- Rejects floating point in note handlers via `FPillegal`.
- Does not attempt to fully update MIPS FP exception status; arithmetic is done in double precision.

Dependencies:
- Depends on Plan 9 `fpi` internal FP library, `Ureg` register layout, MIPS watch registers, cache flush helpers, `Tos.kscr`, and trap handling.

Notable risks:
- Several operations are explicitly unimplemented: sqrt and many newer conditional/reciprocal forms.
- 64-bit DMTC1/DMFC1 paths print warnings that word order may be wrong.
- Watchpoint-assisted delay-slot execution is intricate and globally serialized by `watchlock`.
