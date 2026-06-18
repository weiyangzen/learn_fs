# File Research: sources/os/plan9/9front/sys/src/cmd/5e/seg.c

This file implements emulator segment allocation, address translation, and safe host-buffer copying for locked segments.

Key routines:
- `newseg()` allocates a segment and backing `Ref`+data buffer, sets address range, marks BSS as lock-protected, and installs it in `P->S[idx]`.
- `freesegs()` releases all process segments and shared backing buffers.
- `vaddr()` resolves an emulated address/length to a host pointer, optionally read-locking lock-protected segments, and reports faults through `suicide()`.
- `vaddrnol()` resolves and immediately unlocks.
- `segunlock()` releases a segment read lock if needed.
- `copyifnec()` returns a direct pointer for unlocked memory or copies out locked memory into a host buffer, with string-length support for `len < 0`.
- `bufifnec()` returns a direct pointer for unlocked memory or allocates a temporary output buffer for locked memory.
- `copyback()` writes a temporary buffer back to emulated memory and frees it.

Dependencies and interactions:
- Used heavily by instruction execution and syscall marshalling.
- Locking is designed around BSS/heap growth and host syscalls that may block or mutate memory.

Research relevance:
- Core memory safety and address translation layer for the emulator.

Risk notes:
- `vaddr()` rejects accesses crossing segment boundaries.
- `copyifnec()` with `len < 0` calls `strlen()` on emulated memory after translating only a zero-length access.
- Callers must pair locked direct pointers with `segunlock()` or use copy/buffer helpers correctly.
