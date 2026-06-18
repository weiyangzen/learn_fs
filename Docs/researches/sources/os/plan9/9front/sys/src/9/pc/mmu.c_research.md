# File Research: sources/os/plan9/9front/sys/src/9/pc/mmu.c

Implements 32-bit x86 memory-management setup for the 9front PC kernel. The file defines flat GDT descriptors, per-CPU TSS setup, IDT/GDT loading, CR3 task switching, process page directory management, user PTE insertion, kernel/device mappings, temporary mappings, kmap mappings, and cache-attribute helpers.

Key mechanisms:
- Uses a self-mapped page directory at `VPT` so the kernel can edit current page tables through virtual addresses.
- `mmuinit()` marks kernel text read-only, installs VPT, allocates/configures the TSS, loads GDT/IDT, and switches to the kernel page directory.
- `mmuswitch()`, `flushmmu()`, `mmurelease()`, `putmmu()`, and `checkmmu()` manage per-process user mappings and page-table caches.
- `vmap()`/`vunmap()` maintain global device mappings in the `VMAP` range, with `vmapsync()` lazily copying master mappings from CPU0 page tables into current address spaces.
- `kmap()`/`kunmap()` provide temporary per-process page mappings in the `KMAP` region.
- `tmpmap()`/`tmpunmap()` provide single-page temporary mappings for editing page directories, with a fast path for physical pages already visible through `KZERO`.
- `patwc()` adjusts PAT bits for write-combining mappings, mainly framebuffer use.

Important dependencies include `Page`, `Proc`, `Mach`, `Tss`, `Segdesc`, paging macros from `mem.h`, and low-level routines such as `putcr3`, `invlpg`, `lgdt`, `lidt`, `ltr`, `newpage`, `freepages`, `rampage`, `procflushothers`, and MSR access.

Research notes:
- The file is central to address-space behavior but not filesystem-specific. Storage/display drivers in this group depend on `vmap()`, `vunmap()`, `KADDR()`, and cache-attribute helpers for MMIO and DMA-accessible memory.
- Safety invariants are enforced with panics: kmap reference balance, valid VMAP bounds, no overwriting existing device mappings, TMPADDR not already remapped, and valid kernel physical address conversions.
- The code assumes 32-bit physical addresses for `vmap()` by rejecting ranges where `(pa+size) >> 32` is nonzero.
