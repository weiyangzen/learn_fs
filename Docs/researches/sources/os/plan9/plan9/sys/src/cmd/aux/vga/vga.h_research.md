# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vga.h

Central header for Plan 9 `aux/vga`.

Key definitions:
- VGA I/O port constants for misc/status/feature, sequencer, CRTC, graphics, attribute, palette, pixel mask, and DAC status.
- Standard clocks `RefFreq`, `VgaFreq0`, `VgaFreq1`.
- `Ctlr`: controller module interface with `snarf`, `options`, `init`, `load`, `dump`, type, flags, and linked controller.
- Controller flags:
  - lifecycle flags `Fsnarf/Foptions/Finit/Fload/Fdump/Ferror`,
  - hardware capability/use flags for 2x8, enhanced, parallel VRAM, external SID, clock doubler/divisor, linear addressing, 32-bit SID.
- `Attr`: name/value linked-list database attributes.
- `Mode`: monitor/mode timing, channel, frequency, dimensions, sync, interlace, and attributes.
- `Vga`: full mutable VGA state, including generic registers, palette, two sets of clock fields, memory aperture/base/size, BIOS/PCI matches, mode, virtual screen, controller links, attributes, and private pointer.

Integration:
- Declares all VGA controller modules, RAMDACs, clock chips, helpers, PCI functions, database helpers, I/O helpers, and globals used across `aux/vga`.
- Documents known `virtx` vs `mode->x` pitfalls for older drivers.

Filesystem relevance:
- Indirect: display subsystem header, not filesystem code.
