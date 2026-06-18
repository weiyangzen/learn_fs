# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfj.c

Ghostscript `pdfwrite` image-writing utility implementation. It owns PDF image dictionary fields, image XObject/inline setup, image matrices, raw bitmap copying, filter dictionaries, binary stream finalization, and alternative compression selection.

Key behavior:
- Defines full and short image dictionary key sets, including abbreviated names for inline images.
- Implements GC tracing/relocation for `pdf_image_writer`, including active binary writers, image resources, data streams, named dictionaries, and mask resources.
- `pdf_put_image_values` writes `/ImageMask`, `/Width`, `/Height`, `/BitsPerComponent`, `/ColorSpace`, `/Decode`, `/Interpolate`, and ImageType 4 `/Mask` arrays when supported.
- `pdf_put_image_filters` transfers active filter settings, currently including CCITTFaxDecode parameters through common `pdf_put_filters`.
- `pdf_make_bitmap_matrix` and `pdf_put_image_matrix` create top-to-bottom PDF image placement matrices, adjusting for images that ended before their declared height.
- `pdf_do_image_by_id` and `pdf_do_image` emit image XObject `Do` calls and register image resources for charprocs when needed.
- `pdf_begin_write_image` creates inline COS streams or XObject image resources, handles NI-named image dictionaries, initializes binary writers, and records specified/data image height.
- `pdf_make_alt_stream` creates an additional image stream for alternative compression trials.
- `pdf_begin_image_data` writes image dictionary fields and filter dictionaries for a specific writer stream.
- `pdf_complete_image_data` pads incomplete DCT/PNG image streams with neutral bytes because those encoders cannot safely close with short data.
- `pdf_end_image_binary` closes binary streams or invokes compression selection, then corrects `/Height` if the image data ended early.
- `pdf_end_write_image` writes inline `BI`/`ID`/`EI` images or registers XObject resources, handles named-image dictionary merging, disables encryption for inline image bytes, and supports resource substitution/deduplication.
- `pdf_copy_mask_bits` and `pdf_copy_color_bits` copy raw monobit and device-pixel rows with bit offset/inversion handling.
- `pdf_choose_compression` compares Flate and DCT/alternative streams using a compression chooser and stream lengths, discards the loser, rewires the winning stream into the image resource, and preserves optional mask writer state.

Notable dependencies:
- PDF object/resource helpers from `gdevpdfx.h`, `gdevpdfg.h`, and `gdevpdfo.h`.
- PS/PDF binary writer and image filter setup from `gdevpsds.h`.
- PNG predictor/filter support from `spngpx.h`.

Research notes:
- Inline image writing explicitly sets `pdev->KeyLength = 0` while writing contents so encryption is disabled for inline image data.
- The alternative-compression path assumes stream roles: primary Flate, secondary DCT/other, and a chooser stream; it also contains heuristics for very large size differences.
- Named images created by NI pdfmarks are handled by moving dictionary entries and replacing the NI object contents with the actual image stream object.
- The code comments warn that substituted images with alternate streams may leave unused bytes in `pdev->streams.strm`.
