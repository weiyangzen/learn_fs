# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevtfax.c

## Purpose
Implements Ghostscript TIFF fax and monochrome compressed TIFF devices: `tiffcrle`, `tiffg3`, `tiffg32d`, `tiffg4`, `tifflzw`, and `tiffpack`.

## Main Concepts
- Defines `gx_device_tfax`, combining printer state, fax parameters, TIFF writer state, `MaxStripSize`, and `FillOrder`.
- Uses shared TIFF directory writing from `gdevtifs.c`.
- Uses Ghostscript stream encoders for CCITT Fax, LZW, and PackBits/RLE output.
- Supports stripped TIFF output when `MaxStripSize` limits uncompressed strip size.

## Key Functions
- `tfax_get_params`, `tfax_put_params`: expose and validate `MaxStripSize` and `FillOrder`, delegating fax parameters to `gdevfax`.
- `gdev_stream_print_page_strips`: sends row ranges through a stream encoder and finalizes each TIFF strip.
- `gdev_fax_print_page_stripped`: exported helper for other fax drivers.
- `tifff_print_page`: common fax TIFF page writer.
- `tiffcrle_print_page`, `tiffg3_print_page`, `tiffg32d_print_page`, `tiffg4_print_page`: configure CCITT variants.
- `tifflzw_print_page`, `tiffpack_print_page`: configure LZW and PackBits output.
- `tfax_begin_page`: temporarily patches width for fax-adjusted page width while writing the TIFF directory.

## Dependencies
Uses `gdevprn.h`, `gdevtifs.h`, Ghostscript stream internals, CCITT Fax (`scfx.h`), fax device helpers (`gdevfax.h`), LZW, and RLE stream templates.

## Notable Risks
- Several calls to `gdev_tiff_end_strip` and `gdev_tiff_end_page` ignore return values.
- `tfax_begin_page` return value is ignored in common page paths.
- TIFF strip state assumes the encoder writes exactly the intended row ranges.
- The code mutates device width briefly to write adjusted TIFF metadata.

## Filesystem Relevance
Writes TIFF output files/streams and seeks within them for directory patching. It is not filesystem implementation code.
