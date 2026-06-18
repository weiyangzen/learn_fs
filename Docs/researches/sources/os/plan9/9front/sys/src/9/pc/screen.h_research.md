# File Research: sources/os/plan9/9front/sys/src/9/pc/screen.h

Shared declarations for mouse, VGA, screen, draw, cursor, and low-level VGA support.

Content summary:
- Declares mouse interfaces from `devmouse.c`: cursor state, tracking, acceleration, serial mouse decoders, and last-event timing.
- Defines generic VGA register port constants and palette constants.
- Provides `VGAMEM()`, `vgai()`, and `vgao()` helpers/macros for VGA memory and port I/O.
- Defines display-driver structures:
  - `VGAdev`: device operations for enable/disable/page/linear/drawinit/fill/overlay/flush.
  - `VGAcur`: cursor operations for enable/disable/load/move.
  - `VGAscr`: active screen state, including device, PCI device, cursor, framebuffer physical/virtual address, aperture size, bpp, pitch, geometry, MMIO, palette, memimage backing, acceleration hooks, blanking hook, softscreen, and tilt.
- Declares common screen APIs from `screen.c`, draw integration hooks, VGA helpers, and software cursor functions.
- Defines `ishwimage()` to test whether a `Memimage` uses the active hardware screen data.

Research notes:
- This header is the main contract between generic screen code and hardware-specific VGA/display drivers.
- It also bridges mouse code to screen code through cursor and tracking declarations.
- The framebuffer mapping fields in `VGAscr` are populated by `screen.c` and consumed by device drivers.
