# File Research: sources/os/plan9/9front/sys/src/9/pc/screen.c

Implements PC screen/framebuffer setup and common VGA drawing integration.

Key behavior:
- Maintains global `gscreen` and single `VGAscr vgascreen[1]`.
- Supports screen rotation through `tiltpt()`, `tiltrect()`, `tiltsize()`, `actualscreensize()`, and `setactualsize()`.
- `setscreensize()`/`setscreensize0()` create either a software `Memimage` or a direct framebuffer-backed `Memimage`, initialize pitch/depth metadata, reload draw state, restore cursor, and export boot-screen configuration.
- `screenaperture()` allocates/matches physical framebuffer aperture space and maps it with `vmap()`.
- `attachscreen()` exposes screen memory to draw clients; `flushmemscreen()` copies software-screen damage to linear or paged framebuffers and handles tilted output.
- Palette helpers `getcolor()`, `setpalette()`, and `setcolor()` manage VGA DAC colors for indexed modes.
- Cursor helpers rotate hardware cursor bitmaps when needed and delegate to the active `VGAcur`.
- `hwdraw()` opportunistically uses device fill/scroll acceleration for suitable draw operations.
- `vgalinearaddr()`/`vgalinearpci()` map framebuffers, apply PAT write-combining via `patwc()`, and request MTRR write-combining with `mtrr()`.
- `bootscreeninit()` attaches to a bootloader-provided framebuffer from `*bootscreen`; `bootscreenconf()` records current framebuffer configuration for reboot.

Research notes:
- This file ties together PCI BAR discovery, MMIO mapping, MTRR/PAT cache attributes, draw device state, mouse cursor state, and boot environment propagation.
- It limits framebuffer mapping to 64 MB even if the PCI region is larger.
- Rotation forces `softscreen`, then flushes transformed pixels to the physical framebuffer.
