# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/neomagic.c

Plan 9 `aux/vga` controller module for NeoMagic MagicGraph/MagicMedia laptop graphics adapters. The file describes itself as a fake driver: it wraps generic VGA setup, adds NeoMagic-specific extended CRT/graphics register save/load, derives LCD panel parameters, enables linear/MMIO behavior, and supports 8/16/24 bpp modes.

Key behavior:
- Defines a small `Neomagic` private object holding the matched PCI device and detected panel dimensions.
- `snarf` calls `generic.snarf`, unlocks NeoMagic graphics registers, reads selected extended CRTC and graphics registers into `vga`, matches vendor `0x10C8`, and sets memory size, aperture size, and maximum clock by device ID.
- Supported device IDs include MagicGraph 128 ZV/ZV+, MagicGraph 128 XD, MagicMedia 256 AV/ZX/XL+. Older MagicGraph 128 variants error out as unsupported.
- `options` advertises and enables linear framebuffer support through `Ulinear|Hlinear`.
- `init` calls `generic.init`, infers panel size from graphics register bits, configures LCD-only panel output, optional centering for modes smaller than the panel, extended CRTC offset, system interface control, color mode extension, pitch, palette entries for 16/24 bpp, and forces nonstandard pixel clocks through `vga->misc |= 0x0C`.
- `load` writes key NeoMagic graphics registers around `generic.load`, enables MMIO/linear state, writes panel centering/control registers, and invokes `palette.load` for non-8-bpp modes.
- `dump` prints generic VGA state plus NeoMagic extended CRTC and graphics register ranges.

Notable dependencies:
- Shared `generic` and `palette` controllers from the VGA framework.
- PCI enumeration via `pcimatch`.
- VGA indexed register helpers `vgaxi`, `vgaxo`, direct port I/O, and Plan 9 `sleep`.

Research notes:
- There is a likely switch fallthrough bug in `init`: panel-detection case `2` sets 1024x768 but lacks a `break`, so it falls into case `3` and overwrites the panel as 1280x1024.
- The condition `if(0 && (nm->pci->did == 0x0005) || (nm->pci->did == 0x0006))` effectively selects only DID `0x0006`, because the first half is always false.
- The file exposes `neomagichwgc` as a no-op controller descriptor; hardware cursor implementation is not present here.
