# File Research: sources/os/plan9/9front/sys/src/9/pc/devvga.c

## Purpose
Plan 9 `#v` VGA controller device exposing a `vgactl` control/status file for screen configuration, hardware cursor, acceleration, framebuffer aperture, and VGA driver selection.

## Exposed Interface
- Device table: `vgadevtab`, device character `v`, name `vga`.
- Files:
  - `vgactl`: read status, write textual control commands.
- Commands include:
  - `type <driver>`
  - `size <WxHxD> <chan>`
  - `actualsize <WxH>`
  - `drawinit`
  - `linear <size> [align]`
  - `hwgc <cursor-driver|off>`
  - `hwaccel on|off`
  - `hwblank on|off`
  - `softscreen on|off`
  - `pcidev <tbdf>`
  - `tilt <mode>`
  - `textmode`

## Implementation Notes
- `vgareset()` reserves standard VGA I/O port ranges and finds the first PCI display device.
- `vgaread()` reports active VGA driver type, configured virtual/actual size, tilt, hardware cursor, acceleration/blanking status, aperture address, and softscreen state.
- `vgactl()` is the command dispatcher. It updates global `vgascreen[0]`, calls driver-specific `enable`, `disable`, and `drawinit` hooks, and coordinates screen-image recreation.
- Screen-changing operations use `drawlock`, `deletescreenimage()`, `setscreensize()`, `setactualsize()`, `vgascreenwin()`, and `resetscreenimage()`.
- Hardware cursor changes call `cursoroff()`/`cursoron()` and cursor-driver hooks.
- `CMlinear` requests a framebuffer aperture with `screenaperture()`.

## Filesystem Relevance
This is a canonical Plan 9 control-file driver: graphics device state is configured by writing command strings to a file, and status is read as text. It is not a filesystem implementation, but it illustrates Plan 9 device-file semantics and user/kernel control-plane design.

## Risks / Quirks
- The driver assumes a single VGA screen at `vgascreen[0]`.
- Several commands require prior screen sizing and fail with `"set the screen size first"`.
- Driver lists are external (`vgadev[]`, `vgacur[]`), so behavior depends on platform-linked VGA modules.
