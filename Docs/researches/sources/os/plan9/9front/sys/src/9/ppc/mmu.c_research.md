# File Research: sources/os/plan9/9front/sys/src/9/ppc/mmu.c

PowerPC hashed page-table and MMU PID management.

Key responsibilities:
- Sizes and allocates a per-processor hashed page table, installs SDR1, initializes segment registers, and seeds MMU PID/color state.
- Uses VSIDs derived from per-process MMU PIDs and user segment numbers.
- Runs `mmusweep()` as a background process to age/reclaim stale MMU PID colors and clear matching PTEs from the hash table.
- Allocates new MMU PIDs, flushing all TLBs and resetting process PIDs on wraparound.
- Switches process address spaces by programming segment registers; kernel processes get zeroed user segment registers.
- Inserts or replaces PTEs in hashed PTE groups in `putmmu()`, flushing TLB entries when mappings change and flushing instruction cache for text pages.
- Provides `flushmmu()`, `mmurelease()`, `checkmmu()`, and `cankaddr()`.

Dependencies:
- Uses PPC segment registers, SDR1, TLB flush/load helpers, process table, and shared page/text-flush helpers.

Notable behavior:
- If no MMU PID can be assigned, `putmmu()` schedules until the sweep process catches up.
