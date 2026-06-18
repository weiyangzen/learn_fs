# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mga4xx.c

Implements `aux/vga` support for Matrox G200, G400/G450, and G550 adapters.

Key behavior:
- Defines Matrox PCI IDs, MMIO register offsets, VGA-compatible register windows, RAMDAC indexes, and many bit definitions for CRTC, sequencer, DAC, and pixel-clock control.
- Provides MMIO helpers for sequencer, CRTC, CRTC-extension, DAC, graphics-controller, attribute, and misc registers.
- `mapmga4xx()` sets video type `mga4xx` and attaches `mga4xxmmio` plus an 8 MB or 32 MB framebuffer segment.
- `snarf()` matches Matrox PCI devices, verifies memory-space enable, records revision/device data, maps apertures, and probes framebuffer size.
- `options()` aligns virtual width to 128 pixels.
- `g400_calcclock()` computes G200/G400 PLL settings; the G450/G550 path uses `G450Find*PLLParam`, sorted MNP candidates, lock probing, and fallback writes.
- `init()` validates depth/frequency, rejects interlace, computes detailed power-graphics timing fields, builds VGA/Matrox CRTC registers, computes byte/pixel scaling for 8/16/24/32 bpp, and disables generic VGA loading.
- `load()` sequences display blanking, CRTC2 off, cursor disable, pixel PLL setup, DAC setup, memory mapping, CRTC/extension programming, endian setup for 24/32 bpp, palette initialization, and cursor restoration.
- `dump()` emits register traces via `dump_all_regs()`.

Important details:
- G450/G550 PLL programming is lock-test driven and adapted from XFree86-era code.
- 24 bpp uses special offset and scale calculations; 32/24 bpp also set a big-endian mode register.
- `setpalettedepth()` writes `palettedepth` through `#v/vgactl`, but its string patching only handles one decimal digit cleanly.
- The file contains extensive debug traces and comments documenting historical fixes and supported acceleration assumptions.

Filesystem relevance:
- Directly uses `#v/vgactl` and named video segments exposed by the Plan 9 video device; not filesystem logic, but device-namespace dependent.
