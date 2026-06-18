# File Research: sources/os/plan9/plan9/sys/src/9/bcm/mmu.c

ARMv6 MMU setup and per-process user mapping management.

Key behavior:
- `mmuinit()` builds physical early page tables: maps all DRAM at `KZERO`, identity maps first MB for MMU enable transition, maps MMIO at `VIRTIO`, and maps high exception vectors via an L2 page.
- `mmuinit1()` switches to virtual L1 pointer and removes identity mapping.
- Maintains per-process L2 page tables through `proc->mmul2` and `proc->mmul2cache`.
- `mmuswitch()` flushes caches, clears stale L1 user entries, installs process L2 tables, writes back L1 entries, and invalidates TLB.
- `flushmmu()` marks current process for new TLB and switches.
- `mmurelease()` returns per-process L2 pages to page allocator.
- `putmmu()` allocates L2 tables as needed, installs small-page user mappings with permissions/cacheability, invalidates TLB entry, performs cache maintenance, and flushes text I-cache if needed.
- `cankaddr()` validates direct kernel addressability.
- `mmukmap()` creates section mappings for MMIO/framebuffer-style mappings.

No ASIDs are used beyond a software pid check; this is a simple single-core ARMv6 MMU model.
