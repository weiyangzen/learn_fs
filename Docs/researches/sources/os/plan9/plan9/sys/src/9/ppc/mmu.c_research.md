# File Research: sources/os/plan9/plan9/sys/src/9/ppc/mmu.c

PowerPC hashed-page-table MMU management for single-processor Plan 9.

Key responsibilities:
- Allocates and installs a per-processor hashed page table using SDR1.
- Uses segment registers and VSIDs to distinguish processes.
- Allocates MMU process IDs with color bits and background sweeping.
- `mmusweep` clears stale process IDs from procs and removes matching PTEs from the hash table.
- `mmuswitch` installs user segment registers or clears them for kernel procs.
- `putmmu` inserts or replaces hashed PTEs, flushes stale TLB entries, and performs text-page I/D cache maintenance.
- `flushmmu`, `mmurelease`, `checkmmu`, `countpagerefs`, and `cankaddr` provide required port interfaces.

Important behavior:
- Hash table size is heuristically based on physical memory.
- Process IDs reserve pid 0 and use top pid bits as sweep colors.
- If no MMU pid is available, `putmmu` loops through `sched()` until one is assigned.
- Kernel mappings are expected to come from BATs; only user segments are installed here.

Dependencies:
- Depends on PPC assembly helpers for SDR1, segment registers, TLB flush, cache flush, and process switching.
- Coupled to `fault.c`/`putmmu` caller expectations and `Page.cachectl`.

Notable risks:
- Comment states the design needs modification for multiprocessor use.
- PTE replacement uses a simple rotating slot within a PTEG.
- Background sweeping and pid exhaustion behavior depend on scheduler progress.
