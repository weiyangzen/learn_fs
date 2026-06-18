# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vgasubr.h

## Role

`vgasubr.h` declares helper routines and data tables for programming VGA registers and palettes. It abstracts kernel and standalone access to VGA register mappings.

## Key Interfaces

For kernel builds, `vgaregmap_t` is a pointer to `struct vgaregmap`, which holds a mapped register address, DDI access handle, and mapped flag. For standalone builds, it is a `uint_t`.

The exported functions read and write:
- raw VGA registers,
- CRTC registers,
- sequencer registers,
- graphics-controller registers,
- attribute-controller registers,
- indexed registers,
- DAC colormap entries.

It also exposes `vga_get_hardware_settings()` and debug-only `vga_dump_regs()`.

## Data Tables

The header declares text-mode initialization tables:
- `VGA_ATR_TEXT`
- `VGA_SEQ_TEXT`
- `VGA_CRTC_TEXT`
- `VGA_GRC_TEXT`
- `VGA_TEXT_PALETTES`

It defines register-count constants for each table and `VGA_MISC_TEXT`.

## Research Notes

This is a low-level support header. It expects callers to handle execution context carefully: kernel use involves DDI access handles, while standalone use cannot rely on normal kernel driver services.
