# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsunr.c

## Purpose
Ghostscript printer device for Harlequin-style 1-bit Sun raster output, exposed as `sunhmono`.

## Main Concepts
- Defines the Sun raster header layout and constants for magic, raw pixrect image type, and no colormap.
- Registers `gs_sunhmono_device` as a 1-bit printer device at 72 DPI by default.
- `sunhmono_print_page` writes a binary Sun raster header, page scanlines, 16-bit row padding, and the unusual trailing `"};\n"` terminator.

## Key Behavior
- Computes Ghostscript scanline bytes and rounds output row length up to an even byte count.
- Pulls each raster row with `gdev_prn_get_bits`.
- Writes raw 1-bit data with an extra zero byte when the Ghostscript row size is odd.
- Does not byte-swap the header fields; it writes the host representation of `int` fields.

## Dependencies
Uses Ghostscript printer memory and raster APIs from `gdevprn.h`.

## Notable Risks
- Return values from `fwrite`, `fputc`, and `gdev_prn_get_bits` are not checked after allocation succeeds.
- Header byte order is implicit in native `int` layout, which may not match the Sun raster format on all hosts.
- The output format is intentionally narrow: 1-bit, no colormap, with a nonstandard terminator.

## Filesystem Relevance
Writes an image stream through Ghostscript printer output. It is not filesystem implementation code.
