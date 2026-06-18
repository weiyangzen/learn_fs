# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdtarga.c

IJG `cjpeg` input module for Targa/TGA images, compiled when `TARGA_SUPPORTED` is enabled.

Main data structures and entry points:
- `tga_source_struct` extends `cjpeg_source_struct` with compressor backlink, optional colormap, optional virtual image for row reordering, current row, pixel reader callback, TGA pixel buffer, pixel size, RLE state, and saved row-reader callback.
- `jinit_read_targa` allocates the source and installs `start_input_tga`/`finish_input_tga`.
- `start_input_tga` reads the 18-byte TGA header, validates cmap/type/pixel/interlace constraints, selects RLE or non-RLE pixel input, selects row conversion routine, allocates buffers or a virtual image, skips ID bytes, and reads a 24-bit colormap if present.

Format handling:
- Supports uncompressed and RLE colormapped, truecolor RGB, and grayscale TGA subtypes.
- Supports 8-bit indexed/grayscale, 16-bit 5-5-5 RGB, 24-bit BGR, and 32-bit BGRA input; alpha/attribute byte is ignored.
- Converts 16-bit five-bit channels through `c5to8bits` with rounded expansion.
- Converts BGR input to RGB output.

Row-order behavior:
- Top-down noninterlaced files are streamed through a one-row buffer.
- Bottom-up files are preloaded into a virtual array and reread in top-down logical order.
- Interlaced TGA is rejected.

Filesystem relevance:
- Sequential image-file parser with whole-image buffering for bottom-up orientation. No filesystem logic.
