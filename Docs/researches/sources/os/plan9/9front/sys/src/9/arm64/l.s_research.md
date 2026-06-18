# File Research: sources/os/plan9/9front/sys/src/9/arm64/l.s

Core ARM64 assembly for boot, MMU transition, traps, syscall return, atomics, TLB, FP register movement, and hypercalls.

Key behavior:
- `_start` enters EL1 from EL1/EL2, disables MMU/caches, clears BSS and page tables on CPU 0, builds initial mappings, and enables virtual addressing.
- Establishes per-CPU `Mach`, stack, `TPIDR_EL1`, and static base.
- Provides interrupt priority helpers, atomics, labels, idle wait, cycle reads, and TLB maintenance.
- Provides `touser`, syscall path `vsys0`, trap paths for EL0/EL1, and return paths `forkret`/`noteret`.
- Saves and restores complete trap frames in vector stubs.
- Provides FPU enable/disable and vector register save/load instructions.
- Provides fault-proof `peek` and an `HVC` wrapper.

Dependencies:
- Uses constants from `mem.h` and `sysreg.h`; called by startup, trap, MMU, FPU, and main code.

Research notes:
- Vector stubs are template code patched by `trap.c` to branch to EL0 or EL1 handlers.
- Boot supports both primary and secondary CPU entry.
