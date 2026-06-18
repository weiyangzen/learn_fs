# File Research: sources/os/plan9/9front/sys/src/9/mtx/mmu.c

This file implements the MTX PowerPC hashed page-table MMU management. It uses one page table per processor and distinguishes processes through VSIDs in segment registers.

`mmuinit` sizes the hash table heuristically from physical memory, allocates it aligned to its size, programs `SDR1`, and initializes MMU PID/color reclamation state. `mmuswitch` assigns or reuses a process MMU PID, writes segment registers for eight user segments, and clears them for kernel processes. `newmmupid` allocates a 21-bit PID with high bits used for a color-based reclamation algorithm.

`mmusweep` is a background kproc that sleeps until allocation reaches a trigger color, clears process PIDs with the sweep color, removes corresponding PTEs from the hash table, flushes all TLBs, and advances colors.

`putmmu` installs a mapping into the hashed page table, choosing a slot in the 8-entry PTE group or round-robin replacement, flushes the relevant TLB entry, and flushes data/instruction caches for executable text pages.

Filesystem relevance is direct: memory faults, COW pages, executable images, and memory-mapped file data depend on this mapping path.

Notable risks: the code is explicitly not multiprocessor-ready; when PID allocation runs out, fault/putmmu loops by scheduling until `mmusweep` catches up; hash replacement is simple and may evict within a PTE group.
