# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdrle.c

IJG `cjpeg` input module for Utah Raster Toolkit RLE images, compiled when `RLE_SUPPORTED` is enabled and requiring `<rle.h>`.

Main data structures and entry points:
- `rle_source_struct` extends `cjpeg_source_struct` with visual type, virtual image array, current row, `rle_hdr`, and temporary `rle_pixel` row storage.
- `jinit_read_rle` allocates the source object and sets `start_input_rle`, `finish_input_rle`, and initial `get_pixel_rows = load_image`.
- `start_input_rle` calls `rle_get_setup`, classifies input as grayscale, mapped gray, pseudocolor, truecolor, or directcolor, sets JPEG input metadata, and requests a virtual sample array.
- `load_image` reads the entire RLE image into the virtual array and then switches future row reads to `get_rle_row` or `get_pseudocolor_row`.

Important behavior:
- RLE scanlines are bottom-to-top, so this module buffers the whole image and later reads rows in reverse order to satisfy JPEG top-to-bottom order.
- Alpha is ignored by clearing `RLE_ALPHA`.
- Pseudocolor rows are expanded through a 3-plane colormap; mapped gray/truecolor are colormap-expanded during preload.
- The module deliberately refuses non-8-bit `JSAMPLE` builds with a compile-time syntax error.

Dependencies:
- Uses IJG virtual arrays and optional progress reporting.
- Uses Utah RLE APIs: `rle_hdr_init`, `rle_get_setup`, `rle_getrow`, `RLE_CLR_BIT`.

Filesystem relevance:
- Image decoder adapter only. File interaction is sequential input via the RLE library.
