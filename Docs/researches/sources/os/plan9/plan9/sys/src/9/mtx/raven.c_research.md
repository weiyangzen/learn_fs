# File Research: sources/os/plan9/plan9/sys/src/9/mtx/raven.c

Configures the Motorola Raven PCI host bridge and MPIC interrupt controller for MTX.

Key points:
- Defines the memory-mapped Raven register layout, including device/vendor IDs, mapping windows, watchdogs, and MPIC acknowledge/EIO registers.
- `setmap()` programs Raven address windows for PCI memory, kernel/I/O compatibility mappings, and PCI config/I/O space.
- Uses endian-swapped `mpic32r()`/`mpic32w()` helpers because MPIC registers are accessed with swapped byte order.
- `raveninit()` verifies Raven vendor/device ID (`0x1057:0x4801`), establishes four mapping windows, finds Raven’s PCI config entry, computes MPIC base, masks all 16 interrupt sources, routes them to CPU 0, and enables mixed 8259/Raven interrupt mode.
- `mpicenable()` programs vector priority/route, makes vector 0 level-sensitive for 8259 cascade, and installs EOI handling for nonzero vectors.
- `mpicdisable()`, `mpicintack()`, and `mpiceoi()` implement MPIC control.

Dependencies and interactions:
- Called early from `main()` before interrupt initialization.
- `trap.c` uses `mpicenable()`, `mpicdisable()`, `mpicintack()`, and `mpiceoi()`.
- Depends on PCI enumeration and MTX memory constants from `mem.h`.

Research relevance:
- Board-specific bridge and interrupt controller setup for MTX, connecting PCI and the mixed MPIC/8259 interrupt model.
