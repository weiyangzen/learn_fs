# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgai81x.c

Intel i81x/i830M integrated graphics framebuffer, DPMS blanking, GTT setup, and hardware cursor support.

Key responsibilities:
- Detects supported Intel PCI display IDs including i810/i815-style devices and IBM R31 i830M.
- Maps MMIO BAR1 and registers `i81xmmio`.
- Allocates and installs a graphics translation table through MMIO register `0x2020`.
- Maps framebuffer BAR0 and allocates backing pages, populating device page tables.
- Allocates an uncached page for cursor data and marks its PTE uncached.
- Implements DPMS blanking and 32x32 2bpp hardware cursor.

Important behavior:
- Framebuffer aperture size is capped to 8 MiB.
- Cursor base register uses the physical address of the uncached system-memory cursor page.
- Cursor move uses hardware negative-coordinate flags in position bits.
- Enabling installs `scr->blank = i81xblank` and sets `hwblank`.

Exports:
- `VGAdev vgai81xdev` named `i81x`.
- `VGAcur vgai81xcur` named `i81xhwgc`.

Notable risks:
- Directly manipulates MMU PTE flags for the cursor page.
- Allocated framebuffer backing memory is not freed and is bound to device page-table setup.
- GTT setup assumes register offsets and page-table format for these old Intel chips.
