# File Research: sources/os/plan9/9front/sys/src/9/arm64/mmu.c

ARM64 runtime MMU mapping and per-process address-space switching.

Key behavior:
- Allocates per-CPU user top-level tables in `mmu1init`.
- Converts between direct-mapped physical and virtual addresses.
- Provides `kmapram`, `mmukmap`, `vmap`, and no-op `vunmap`.
- Builds kernel mappings with block pages when possible and page mappings otherwise.
- Walks/allocates process page tables from `up->mmufree`.
- Allocates ASIDs from a 256-entry table and invalidates stale ASID mappings.
- Installs user PTEs in `putmmu`, including text-cache synchronization.
- Switches TTBR0 with ASID tagging and releases process page tables.

Dependencies:
- Uses cache/TLB helpers, page allocator, process MMU fields, and constants from `mem.h`.

Research notes:
- `putasid` proactively switches away from a sleeping process’s page tables on SMP to avoid stale table pages on another CPU.
