# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vgareg.h

## Role

`vgareg.h` defines legacy VGA I/O port offsets, memory ranges, text-mode dimensions, register indexes, and bitfield helpers used by VGA console/framebuffer code.

## Key Definitions

The file defines:
- VGA register base `0x3c0`, register window size `0x20`.
- VGA memory base `0xa0000`, memory size `0x20000`.
- text mode dimensions of 80 columns by 25 rows.
- 8-bit graphics depth and colormap-entry counts.

It enumerates register offsets for:
- attribute controller,
- miscellaneous output,
- sequencer,
- DAC,
- graphics controller,
- CRTC,
- CGA status.

It also defines many register bit masks and packing helpers for horizontal/vertical timings, overflow bits, sync timing, scanline registers, display enable, memory mode, graphics mode, attribute mode, palette selection, and text framebuffer bases.

## Integration Points

Consumers pair this header with `vgasubr.h`, which provides functions for accessing indexed VGA registers. The constants are used by low-level console, boot, and framebuffer paths that need direct VGA programming.

## Research Notes

The macros are hardware-layout definitions, not type-safe APIs. Callers must understand indexed-register addressing and preserve reserved bits where required. This header is also relevant to standalone code paths that run before normal kernel services are available.
