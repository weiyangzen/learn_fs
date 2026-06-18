# File Research: sources/os/plan9/9front/sys/src/9/lx2k/l.s

LX2K ARM64 boot, MMU, trap, syscall, interrupt, atomic, cache/TLB, FPU, and SMC assembly. `_start` enters with physical addressing, switches from EL2 to EL1 if needed, disables MMU/caches, clears page tables/BSS on CPU 0, calls `mmuidmap`/`mmu0init`, enables the MMU, moves into the kernel virtual address range, and calls `main`.

`mmuenable` programs MAIR, TCR, TTBR0/TTBR1, enables I/D caches and MMU, and returns to virtual addresses. The file includes DAIF-based `spl*`, WFI idle, virtual/performance cycle counters, labels, atomics via LDXR/STXR, TTBR writes, local/broadcast TLB invalidations, FP/SIMD save/restore, user entry, syscall return, note/fork return, EL0/EL1 trap frame setup, vector stubs patched by C code, fault-proof `peek`, and PSCI/SMC call support.

Notable risks: the vector stubs contain self-branches intended to be patched; trap-frame offsets and `TRAPFRAMESIZE` must exactly match `Ureg`; EL2 setup assumes a specific boot environment.
