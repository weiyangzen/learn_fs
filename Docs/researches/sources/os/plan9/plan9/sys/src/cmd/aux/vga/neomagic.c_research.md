# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/neomagic.c

Implements a simple NeoMagic laptop VGA backend for MagicGraph/MagicMedia chipsets.

Key behavior:
- `snarf()` runs generic VGA snarfing, unlocks NeoMagic extended registers, captures extended CRTC and graphics registers, matches PCI vendor `0x10C8`, and sets maximum clock, VRAM size, and aperture size by device ID.
- `options()` advertises linear framebuffer support.
- `init()` starts from generic VGA init, derives native panel size, configures LCD-only panel mode, centering/stretch controls, extended color mode, pitch, offsets, and palettes for 8/16/24 bpp.
- `load()` writes required NeoMagic extended registers around `generic.load()`, enables MMIO/linear flags, and loads a palette for non-8-bit modes.
- `dump()` prints generic VGA state plus captured NeoMagic extended CRTC/graphics registers.

Important details:
- Several device IDs are supported; older MagicGraph 128 variants are explicitly rejected.
- The switch that maps graphics register panel size lacks a `break` after the 1024x768 case, so that case falls through to 1280x1024.
- Hardware cursor controller `neomagichwgc` is only a named stub.
- The file calls itself a “fake” driver, reflecting narrow mode-setting support rather than full acceleration.

Filesystem relevance:
- Indirect: used by `aux/vga` to configure Plan 9 display devices and linear video memory, not filesystem behavior.
