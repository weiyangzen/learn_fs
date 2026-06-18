# File Research: sources/os/plan9/9front/sys/src/9/xen/mmu.c

Xen paravirtual x86 MMU management.

Purpose:
- Maintains kernel and process page tables under Xen’s pinned page-table rules.
- Maps Xen machine frames and handles PAE/non-PAE switching.

Key behavior:
- `mmumapcpu0` detects PAE from Xen magic, initializes machine/physical mappings, and maps CPU0 Mach.
- `mmuinit` maps remaining guest memory and switches to the proper stack/page table context.
- `mmuflushtlb` switches page tables with Xen hypercalls or updates PDPT entries in PAE mode.
- `mmupdballoc`, `putmmu`, `mmuptefree`, `mmuswitch`, and `mmurelease` allocate, pin, update, unpin, recycle, and flush process page-directory/page-table pages.
- `mmuwalk` walks or creates kernel page-table entries for mappings.
- `mmumapframe` maps Xen machine frame numbers into fixed virtual slots.

Integration:
- Called by `main.c`, `devxenstore.c`, `uartxen.c`, grant/event-channel code, and VM fault paths.

Risks/notes:
- Comments document Xen refusing to pin pages still mapped writable by stale process tables; code loops around “bad” pages.
- SMP is not supported; several comments say PDB handling would need changes for multiprocessor guests.
