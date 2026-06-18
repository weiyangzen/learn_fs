# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/clgd542x.c

Controller backend for Cirrus Logic CL-GD542x/543x/5446/5480 and related chips.

Core behavior:
- Unlocks Cirrus extended registers.
- Saves sequencer, graphics, CRTC, chip ID, and hidden DAC register.
- Identifies chip family by CRTC ID and sets maximum clock.
- Determines memory size from chip-specific register layouts.
- Enables linear support for PCI/selected chips.
- Supports depths up to 8 bpp.
- Computes programmable VCLK using `clgd54xxclock()`.
- Programs Cirrus VCLK, packed-pixel mode, FIFO threshold, overflow bits, interlace, and linear graphics settings.

Shared behavior:
- `clgd54xxclock()` is exported and reused by `clgd546x.c`.

Ctlrs:
- `clgd542x`
- `clgd542xhwgc` placeholder.

Notable risks:
- Comments say 543x added capabilities are not used.
- Linear aperture handling is broad and uses a 16 MB apparent size when requested.
