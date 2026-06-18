# File Research: sources/os/plan9/9front/sys/src/9/mt7688/fpimips.c

This file implements software MIPS floating-point emulation for the MT7688 port, which targets a MIPS 24K/24KE-class system where hardware FPU may be absent or disabled. It decodes COP1 instructions, emulates floating arithmetic through the common `fpi` internal representation, handles FP loads/stores, FP register/control-register moves, conversions, comparisons, and FP conditional branches.

Important structures are `Instr`, which captures decoded COP1 fields plus converted operands and user state, `FP1`/`FP2` unary/binary operation tables, and `FPcvt` conversion handlers. The emulator preserves MIPS raw FP register semantics: 32 raw 32-bit FP registers, paired even/odd registers for doubles, with explicit attention to word ordering on this little-endian variant.

The central public entry is `fpuemu(Ureg*)`, called from `trap.c` on coprocessor-unusable traps. It validates the faulting PC, handles branch-delay slots, initializes emulated FP state via `fpinit`, repeatedly emulates adjacent FP instructions and NOPs, updates `Ureg.pc`, and posts a note on failure. `fpwatch(Ureg*)` completes the watchpoint-based path used when an FP branch’s delay-slot instruction must run in user mode.

Instruction support includes `LWC1`, `LDC1`, `SWC1`, `SDC1`, `MFC1`, `MTC1`, `CFC1`, `CTC1`, arithmetic add/sub/mul/div, `MOV`, `ABS`, `NEG`, selected rounding/conversion operations, comparisons, and FP branches. Missing operations call `unimp`, generating a user-visible debug note.

The file is not filesystem code, but it is part of the CPU exception substrate that lets user processes execute reliably. That matters to filesystem workloads because page faults, syscalls, and user notes share the same trap/ureg machinery; bad FP emulation can corrupt user register state or trap recovery in filesystem servers.

Notable risks: numeric exception/status behavior is partial, some 64-bit `DMTC1`/`DMFC1` paths print warnings about possible word ordering, and branch-delay-slot execution uses a process FP scratch area plus hardware watchpoints, so correctness depends on the MIPS watch register and ASID behavior matching `mmu.c`.
