# File Research: sources/os/plan9/plan9/sys/src/9/pc/devvga.c

Read completely: 500 lines.

This file implements the Plan 9 VGA control device `#v`.

Key behavior:
- Reserves standard VGA I/O register ranges.
- Exposes VGA BIOS memory, screen control, and optional overlay interfaces.
- `vgactl` accepts commands to select VGA driver, cursor mode, screen size, palette depth, blanking, panning, hardware acceleration, and linear aperture setup.
- `vgabios` reads from low physical address space via `kaddr(0)`.
- Overlay operations dispatch through the active `VGAdev`.

Important interfaces:
- Device name: `vga`, rune `'v'`.
- Files:
  - `vgabios`
  - `vgactl`
  - `vgaovl`
  - `vgaovlctl`
- Uses global screen state from `screen.h`, including `vgascreen`, `physgscreenr`, `blanktime`, `hwaccel`, `hwblank`, and `panning`.

Research notes:
- `checkport()` allows VGA standard ports and otherwise requires unused I/O ranges.
- `CMsize` validates draw channel/depth consistency before resizing screen image state.
- Overlay control sends synthetic `openctl` and `closectl` messages to the active VGA device.
