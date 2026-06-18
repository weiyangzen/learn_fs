# File Research: sources/os/plan9/9front/sys/src/9/mt7688/mmu.c

This file implements MT7688 MIPS MMU management: hardware TLB initialization, kernel temporary mappings, per-process ASID allocation, software TLB population, TLB purging, and instruction-cache flushing after text mappings.

`tlbinit` invalidates all hardware TLB entries. `kmapinit`, `kmap`, `kunmap`, `kfault`, and `kmapinval` implement the KSEG3-based kmap mechanism for mapping physical pages with cache-color-aware virtual addresses. `putktlb` places kmap entries into hardware TLB entries, initially preserving a small wired range until startup completes.

For user mappings, `mmuswitch` assigns or reuses per-process ASIDs, writes TLB entry 0 to set current PID, and handles `newtlb`. `putmmu` writes a `Softtlb` entry, installs a matching hardware TLB entry, and flushes I-cache for text pages when needed. `purgetlb` invalidates stale ASIDs in process tables, the software TLB, and hardware TLB entries.

Filesystem relevance is direct to page-cache and memory-mapped file behavior. `faultmips`/`fault` ultimately call into this code to install translations for executable text, data, stack, and COW pages; `kmap` is used for kernel access to physical pages during I/O and filesystem operations.

Notable risks: the fast assembly TLB refill path depends on `Softtlb` layout/hash matching this C code; kmap exhaustion retries with diagnostics; cache coloring is manually encoded through `PIDX`.
