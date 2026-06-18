# File Research: sources/os/plan9/9front/sys/src/9/bcm64/l.s

ARM64 BCM bootstrap, exception vectors, atomics, cache/TLB, FP register, and fault-safe copy assembly.

Key responsibilities:
- Boots from physical mode, selects EL1/EL2 setup, disables MMU, clears BSS/page tables, builds initial mappings, enables MMU/caches, and calls `main`.
- Computes CPU index from `MPIDR_EL1` and sets per-CPU `Mach` pointer in `TPIDR_EL1`.
- Provides `sev`, interrupt priority functions, idle wait, atomics, label save/restore, and return trampolines.
- Implements TTBR/TLB maintenance helpers and cache maintenance helpers.
- Provides FP/SIMD enable/disable and full V-register save/restore.
- Implements EL0/EL1 syscall/trap/IRQ/FIQ/SERR vector paths and return paths.
- Provides fault-proof `peek()` copy loop used by trap/fault probing.

Important behavior:
- Vector dispatch branches are patched to user/kernel-specific handlers.
- Uses `TRAPFRAMESIZE` layout from `mem.h`.
- Broadcast TLB operations use inner-shareable barriers where appropriate.

Dependencies:
- ARM64 system registers, `mem.h`, MMU C setup, trap/syscall C handlers, and Plan 9 calling conventions.
