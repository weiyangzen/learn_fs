# File Research: sources/os/plan9/9front/sys/src/9/sgi/l.s

Main SGI/MIPS assembly support file. It contains boot entry `start`, ARCS firmware call trampoline, user-mode entry, interrupt priority routines, label save/restore, TLB register access, soft-TLB hash/miss fast path, general exception vector save/restore, FP save/restore, atomics, cache flushes, block output, and CP0 count/compare accessors.

The UTLB miss path hashes `TLBVIRT`, checks `m->stb`, installs even/odd TLB entries, and falls back to the general exception path on miss/collision. `saveregs`/`restregs` define the `Ureg` stack frame consumed by `trap.c`.

This file is ABI-critical with `dat.h`, `mem.h`, and `ureg.h`: register globals, `Mach` offsets, UREG offsets, and cache/TLB constants must remain aligned.
