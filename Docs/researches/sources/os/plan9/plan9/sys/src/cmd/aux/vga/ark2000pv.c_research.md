# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/ark2000pv.c

VGA controller backend for ARK Logic ARK2000PV GUI accelerator.

Core behavior:
- Unlocks extended sequencer registers.
- Saves sequencer, CRT, and coprocessor status registers.
- Derives memory size from sequencer register bits.
- Supports linear framebuffer, pixel-clock 2x8 behavior, 1-bit and 8-bit modes.
- Handles overflow bits, interlace registers, memory configuration, aperture setup, FIFO/pitch control, and clock select bits.

Important functions:
- `snarf()` snapshots ARK-specific state.
- `options()` advertises `Hlinear|Hpclk2x8`.
- `init()` validates depth and computes extended register values.
- `load()` writes clock selection carefully and applies linear aperture settings.
- `dump()` prints ARK extended registers.

Ctlrs:
- `ark2000pv`
- `ark2000pvhwgc` placeholder.

Notable risks:
- Comments mention bugs for `1024x768x1` and hardware cursor in 1-bit modes.
- Contains a timing workaround for `w30c516` RAMDAC by toggling sequencer with sleep.
