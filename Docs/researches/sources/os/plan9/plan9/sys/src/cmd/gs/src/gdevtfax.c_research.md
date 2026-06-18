# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevtfax.c

Implements TIFF/Fax and monochrome compressed TIFF printer devices: `tiffcrle`, `tiffg3`, `tiffg32d`, `tiffg4`, `tifflzw`, and `tiffpack`.

Key behavior:
- Defines `gx_device_tfax`, combining printer state, fax state, TIFF writer state, `MaxStripSize`, and TIFF `FillOrder`.
- Exposes `MaxStripSize` and `FillOrder` through get/put parameters; rejects negative strip sizes and fill-order values other than TIFF values 1 and 2.
- Splits page output into strips with `gdev_stream_print_page_strips`, calling a stream filter per strip and then `gdev_tiff_end_strip`.
- Exports `gdev_fax_print_page_stripped` for other fax-style drivers to write CCITT/Fax streams in TIFF strips.
- Builds a sorted monochrome TIFF directory template with bits-per-sample, compression, photometric interpretation, fill order, samples-per-pixel, and T4/T6 options.
- `tifff_print_page` writes the TIFF page directory, configures `FirstBitLowOrder` from `FillOrder`, streams fax rows, and finalizes the TIFF page.
- Configures CCITT RLE, Group 3 1D, Group 3 2D, and Group 4 variants by setting stream state fields such as `EndOfLine`, `EncodedByteAlign`, and `K`, plus the proper TIFF compression/options tags.
- Implements LZW and PackBits TIFF output through Ghostscript stream templates `s_LZWE_template` and `s_RLE_template`.
- `tfax_begin_page` temporarily patches the device width when fax encoding columns differ from the current device width.

Dependencies:
- Uses `gdevprn.h`, `gdevtifs.h`, `strimpl.h`, `scfx.h`, `gdevfax.h`, `gdevtfax.h`, `slzwx.h`, and `srlx.h`.
- Relies on the shared TIFF directory/strip writer in `gdevtifs.c` and fax-stream helpers from the Ghostscript fax subsystem.

Research notes:
- `MaxStripSize` is based on uncompressed byte count and falls back to one row per strip if the requested maximum is smaller than a scan line.
- The code intentionally avoids the `CleanFaxData` TIFF tag because many TIFF readers do not recognize it.
