# File Research: sources/os/plan9/plan9/sys/src/9/pc/screen.h

Shared declarations and types for PC screen, VGA devices, cursors, mouse linkage, and draw integration.

Key elements:
- Defines `Cursorinfo`.
- Declares mouse tracking and serial mouse packet functions.
- Defines generic VGA port constants and palette constants.
- Defines `VGAdev` driver operations: enable/disable/page/linear/drawinit/fill/overlay/flush.
- Defines `VGAcur` cursor operations: enable/disable/load/move.
- Defines `VGAscr`, the main VGA screen state, including PCI pointer, framebuffer address/size, MMIO, colormap, current screen image, acceleration hooks, blanking, and driver-private ID.
- Declares screen, cursor, software cursor, draw, and VGA helper functions.
- Defines `ishwimage` helper macro.

Interactions:
- Included by `screen.c`, `mouse.c`, `psaux.c`, and VGA driver files.
- Bridges PC-specific VGA code with portable draw/devmouse code.

Research notes:
- Header-only graphics/input contract.
