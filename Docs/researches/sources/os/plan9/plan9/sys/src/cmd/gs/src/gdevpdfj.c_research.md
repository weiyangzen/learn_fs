# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfj.c

Ghostscript `pdfwrite` image-writing utilities. This file owns image dictionaries, inline/XObject setup, placement matrices, raw bitmap copying, filter output, stream finalization, and alternative compression selection.

Key behavior:
- Defines full and abbreviated image dictionary key sets.
- Implements GC tracing/relocation for `pdf_image_writer`.
- `pdf_put_image_values` writes image mask, dimensions, bits per component, color space, decode arrays, interpolation, and ImageType 4 `/Mask` arrays when supported.
- `pdf_put_image_filters` transfers active image filter settings through common PDF filter output.
- `pdf_make_bitmap_matrix` and `pdf_put_image_matrix` create top-to-bottom PDF image matrices, adjusted for short image data.
- `pdf_do_image_by_id` and `pdf_do_image` emit XObject `Do` calls and register XObject use for charprocs.
- `pdf_begin_write_image` creates inline streams or XObject image resources, handles named image dictionaries, and initializes binary writers.
- `pdf_make_alt_stream` creates an extra stream for alternative compression trials.
- `pdf_begin_image_data` writes dictionary values and filter dictionaries for each active writer stream.
- `pdf_complete_image_data` pads incomplete DCT/PNG streams with neutral bytes before close.
- `pdf_end_image_binary` closes binary streams, chooses compression when needed, and corrects `/Height` for short data.
- `pdf_end_write_image` writes inline `BI`/`ID`/`EI` images or registers XObject resources, handles NI dictionary merging, disables encryption for inline image bytes, and supports resource substitution.
- `pdf_copy_mask_bits` and `pdf_copy_color_bits` copy raw monobit and device-pixel rows.
- `pdf_choose_compression` compares Flate and alternative streams, discards the loser, and rewires the winning stream into the image resource.

Research notes:
- Inline image bytes are written with `KeyLength` temporarily set to zero so they are not encrypted.
- The alternative compression path assumes stream roles for Flate, DCT/other, and chooser streams.
- Named images from NI pdfmarks are merged into the real image stream object.
