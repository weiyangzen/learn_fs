# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/mga4xx.c

Plan 9 `aux/vga` controller module for Matrox MGA G200/G400/G450/G550 adapters. It implements PCI discovery, MMIO/framebuffer segment attachment, VRAM probing, Matrox CRTC/DAC/sequencer register calculation, pixel PLL programming, mode loading, palette setup, and controller descriptors for `mga4xx` plus a mostly-dump-only `mga4xxhwgc`.

Key behavior:
- Defines register offsets and bit fields for Matrox PCI config registers, control aperture VGA-compatible registers, CRTC extension registers, RAMDAC indexes, pixel PLLs, and mode-control bits.
- Uses an `Mga` private state object to store PCI identity, mapped MMIO/framebuffer pointers, probed framebuffer size, PLL fields, PCI option registers, computed VGA/Matrox register images, timing fields, and aperture size.
- `snarf` finds Matrox PCI device IDs `MGA4XX`, `MGA550`, or `MGA200`, verifies memory-space enablement, maps `mga4xxmmio` and `mga4xxscreen`, enters MGA mode, and probes VRAM in 2 MiB steps by write/read tests through the framebuffer.
- `init` validates depth and non-interlace constraints, computes timing fields from `Mode`, computes pixel PLL settings for G200/G400 or stores requested frequency for G450/G550, builds VGA CRTC and CRTC-extension register images, initializes sequencer/graphics/attribute images, and disables generic `vga*` load hooks because this driver needs a custom order.
- `load` writes sequencer, attribute, graphics, DAC, PLL, CRTC, and CRTC-extension state in a hardware-specific sequence: video off, cursor off, PLL programming, DAC mode selection for 8/16/24/32 bpp, CRTC load, MGA mode enable, framebuffer endian setup for 24/32 bpp, mapping enable, screen enable, palette initialization, and cursor restore.
- G450/G550 PLL code builds and sorts candidate M/N/P values, tests lock stability around candidate offsets, and writes the best usable MNP triplet.

Notable dependencies:
- Plan 9 VGA framework types and helpers from `vga.h`, including `Vga`, `Ctlr`, `Mode`, `trace`, `vgactlpci`, `vgactlw`, `resyncinit`, and shared controller linkage.
- PCI helpers from `pci.c`/`pci.h`: `pcimatch`, `pcicfgr8`, `pcicfgr32`.
- Plan 9 segment attachment for hardware mappings via `segattach`.

Research notes:
- This is low-level display hardware initialization code, not filesystem code, but it is in the subset A 9front tree.
- Several hardware waits are unbounded busy loops, especially PLL-lock waits. A non-locking or wedged device could hang the utility.
- The VRAM probe writes test bytes into framebuffer memory. It restores only the CRTC extension mode bit, not previous framebuffer contents at tested offsets.
- `options` aligns `vga->virtx` to 128 pixels, which affects pitch and mode memory layout.
- `setpalettedepth` accepts 16 but is called only for 8 bpp in this file.
- The code uses many constants and comments adapted from old XFree86/Matrox references; behavior is tightly coupled to early-2000s hardware assumptions.
