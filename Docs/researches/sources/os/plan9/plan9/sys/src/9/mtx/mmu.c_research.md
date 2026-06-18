# File Research: sources/os/plan9/plan9/sys/src/9/mtx/mmu.c

Implements the MTX PowerPC hash-page-table MMU support and MMU PID aging.

Key points:
- Uses one hash page table per processor; process address spaces are distinguished by VSID fields in segment registers.
- Sizes the page table heuristically from ROM-provided `memsize`, allocates it aligned with `xspanalloc()`, writes SDR1, and initializes MMU PID/color state.
- Defines 21-bit MMU PIDs with two high color bits. PID 0 is reserved.
- `mmusweep()` is a background kernel process that waits for trigger color, clears stale proc `mmupid`s of the sweep color, invalidates matching hash PTEs, flushes all TLBs, and advances sweep/trigger colors.
- `newmmupid()` allocates the next PID, wakes the sweep process near color boundaries, and returns 0 if no safe PID is available.
- `flushmmu()` marks the current proc for a new TLB context and calls `mmuswitch()`.
- `mmuswitch()` sets segment registers for user procs using `VSID(pid, segment)` or clears them for kernel procs.
- `putmmu()` hashes `(vsid, va)` into a PTE group, replaces or inserts a PTE, flushes the specific TLB entry, and handles per-page cache-control states (`PG_NOFLUSH`, `PG_TXTFLUSH`).
- `cankaddr()` reports how much physical memory can be addressed through `KADDR()`.

Dependencies and interactions:
- Spawned by `main.c` as `mmusweep`.
- Called from fault handling to install translations.
- Uses page cache flush states established by text loading and segment code.
- Depends on assembly helpers for segment register, SDR1, TLB, D/I-cache operations.

Research relevance:
- Core virtual-memory implementation for the MTX PowerPC port, including its PID recycling scheme.
