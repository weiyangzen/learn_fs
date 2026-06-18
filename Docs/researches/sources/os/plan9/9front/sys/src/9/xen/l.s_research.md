# File Research: sources/os/plan9/9front/sys/src/9/xen/l.s

Xen x86 assembly bootstrap, low-level CPU helpers, hypercall glue, and vector stubs.

Purpose:
- Entry point from Xen’s Linux-style builder.
- Provides x86 low-level primitives for the Xen Plan 9 kernel.

Key behavior:
- `_start` records `xentop` and `xenstart`, clears flags, maps CPU0 Mach through `mmumapcpu0`, sets stack/SB, and enters C `main`.
- Defines common x86 helpers: CPUID/MSR/TSC, spl, atomic exchange, labels, halt/idle, FPU save/restore, string I/O stubs or routines as needed.
- Provides Xen-specific page-table update wrappers and hypercall dispatch helpers.
- Builds a dense `vectortable` of 256 six-byte vector entries, routing most vectors to stray handling and syscall vector to `_syscallintr`.

Integration:
- Works with `trap.c`, `plan9l.s`, `mmu.c`, and hypervisor ABI definitions.

Risks/notes:
- Vector-entry size is assumed by `trapinit`, which advances by 6 bytes per vector.
- Much code is inherited x86 kernel machinery adapted for Xen paravirtual constraints.
