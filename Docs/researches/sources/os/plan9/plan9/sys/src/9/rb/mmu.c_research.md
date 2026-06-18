# File Research: sources/os/plan9/plan9/sys/src/9/rb/mmu.c

RouterBoard MIPS MMU management for hardware TLB invalidation, color-aware temporary kernel mappings, software TLB entries, ASID allocation, user mapping insertion, and TLB purge.

Key responsibilities:
- Initializes all hardware TLB entries as invalid in `tlbinit`.
- Manages the fixed `KMap` pool used by `kmap`/`kunmap`, including per-Mach active mappings and TLB entries.
- Chooses kmap virtual addresses that preserve cache index/color bits to avoid MIPS virtual coherence exceptions.
- Handles kernel kmap faults from KSEG3 through `kfault`.
- Allocates per-process TLB PIDs/ASIDs with `newtlbpid`, switches ASIDs in TLB entry 0 in `mmuswitch`, and purges dead ASIDs in `purgetlb`.
- Inserts user mappings in both the software TLB hash and hardware TLB through `putmmu`, applying the port cacheability policy and page cache-flush state.
- Provides stubs or simple implementations for `checkmmu`, `countpagerefs`, and `cankaddr`.

Important behavior:
- During startup, kmap entries use a small wired TLB range; after `up` becomes non-nil, the code shares all but one TLB entry between kernel and user mappings.
- `putstlb` hashes even/odd page pairs by virtual address plus ASID and tracks hash collisions.
- `purgetlb` invalidates software and hardware entries for ASIDs no longer owned by live processes.

Dependencies and assumptions:
- Depends on MIPS CP0/TLB helpers (`puttlb`, `puttlbx`, `gettlbp`, `gettlbvirt`, `tlbvirt`, `setwired`) and on the `Softtlb` layout used by assembly TLB-miss code.
- Assumes direct KSEG0/KSEG1 mappings for normal physical memory and fixed `MEMSIZE`.

Notable risks:
- `NWTLB` is zero, so `wiredpte` will panic if used.
- KMap pool exhaustion spins through `kmapinval` and retries, printing diagnostic timing if starved.
- Software-TLB hash collisions overwrite prior entries and rely on refault/reload behavior.
