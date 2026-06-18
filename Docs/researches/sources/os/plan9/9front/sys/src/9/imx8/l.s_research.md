# File Research: sources/os/plan9/9front/sys/src/9/imx8/l.s

Role: i.MX8 ARM64 bootstrap, low-level CPU/MMU/cache/TLB/FPU/syscall/trap assembly, and SMC bridge.

Key responsibilities:
- `_start` preserves boot argument, sets SB, enters EL1 from EL2 if needed, disables MMU, flushes caches, computes `machno`, sets `Mach` pointer/stack, clears L1/BSS on CPU 0, builds initial maps, enables MMU, sets `TPIDR_EL1`, then calls `main`.
- `svcmode` configures EL2 state, timer offset, HCR, SCTLR_EL2, VTTBR, and returns to EL1.
- `mmuenable` sets MAIR/TCR, TTBR0/TTBR1, enables SCTLR MMU/cache bits, switches stack/LR to high virtual addresses, and invalidates I-cache.
- Provides atomics (`cmpswap`, `tas`), barriers (`coherence`), interrupt priority (`spl*`, `islo`), idle `WFE`, cycle counters, labels, FAR/TTBR access.
- Provides broadcast/local TLB maintenance entry points.
- Provides FPU enable/disable and raw vector register save/load.
- Implements EL0 syscall fast path, trap path, fork/notereturn, EL1 trap return, and vector stubs patched to user/kernel handlers.
- Provides fault-proof byte copy `peek` and `smccall()` for PSCI/SMC calls.

Dependencies:
- Tightly coupled to `mem.h` constants, `Mach` offsets from `dat.h`, ARM64 sysreg definitions, and C functions `main`, `trap`, `syscall`, `mmuidmap`, `mmu0init`.

Notes:
- Exception vectors store a trap frame of `TRAPFRAMESIZE` and route through C with `Ureg`.
- Several vector branch sites are self-loop placeholders intended to be patched elsewhere.
