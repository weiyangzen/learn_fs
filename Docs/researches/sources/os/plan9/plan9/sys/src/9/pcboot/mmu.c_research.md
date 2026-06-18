# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/mmu.c

This file implements the 32-bit x86 MMU setup and mapping services used by the Plan 9 pc bootstrap kernel. It defines the kernel GDT, initializes per-CPU TSS/GDT/IDT state, switches page directories, maintains per-process user page tables, and manages special kernel virtual regions below `KZERO`.

Key responsibilities:
- Establishes the bootstrap memory layout described in the file header: kernel direct map above `KZERO`, virtual page table at `VPT`, per-process temporary `KMAP`, global device mapping range `VMAP`, and one-page `TMPADDR` mapping.
- `mmuinit0` and `mmuinit` install GDT/TSS/IDT state and self-map the page directory at `VPT`.
- `memglobal` marks kernel PDE/PTE entries with `PTEGLOBAL` when the CPU supports PGE.
- `mmuswitch`, `mmurelease`, `putmmu`, and `checkmmu` maintain per-process page-directory and page-table state.
- `mmuwalk`, `pdbmap`, `pdbunmap`, `vmap`, `vunmap`, and `vmapsync` build and synchronize kernel/device mappings.
- `kmap` and `kunmap` provide temporary per-process mappings for individual physical pages.
- `tmpmap` and `tmpunmap` provide a single safe mapping for editing page directories before they are installed.

Important implementation details:
- The page directory self-map lets page tables be edited through `vpt[]` and `vpd[]`.
- Device mappings are globally allocated from `VMAP` using the bootstrap processor’s page directory as the master copy; other processors/processes fault them in via `vmapsync`.
- `vunmap` invalidates copied mappings by forcing process TLB refreshes and setting per-CPU flush flags.
- `putmmu` deliberately runs at high interrupt priority because faults against the VPT during process switching were historically fragile.
- `KADDR` and `PADDR` are wrapped by checked functions `kaddr` and `paddr`.

Filesystem/storage relevance:
- Kernel buffer cache, device drivers, DMA paths, and page-backed VFS data rely on `kmap`, `vmap`, and correct page-table synchronization.
- Device memory mappings created here are used by low-level storage and network drivers during boot and runtime.
