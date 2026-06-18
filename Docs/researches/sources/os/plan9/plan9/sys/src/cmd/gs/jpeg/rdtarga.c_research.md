# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdtarga.c

IJG `cjpeg` source adapter for Targa/TGA input, compiled only under `TARGA_SUPPORTED`.

Supported input forms:

- Uncompressed or RLE-coded colormapped images with 8-bit indexes and 24-bit BGR colormaps.
- Uncompressed or RLE-coded truecolor images with 16-bit 5-5-5, 24-bit BGR, or 32-bit BGRA pixels.
- Uncompressed or RLE-coded 8-bit grayscale images.
- Non-interlaced top-down files directly, and bottom-up files via a full-image virtual array.

Key functions:

- `read_byte()`, `read_colormap()`, `read_non_rle_pixel()`, and `read_rle_pixel()` provide byte and pixel-level TGA input.
- `get_8bit_gray_row()`, `get_8bit_row()`, `get_16bit_row()`, and `get_24bit_row()` expand TGA pixels into libjpeg grayscale or RGB rows. The 16-bit path uses `c5to8bits[]` to round 5-bit color channels to 8-bit samples.
- `preload_image()` reads bottom-up images into `whole_image`, then switches to `get_memory_row()` to return rows in JPEG order.
- `start_input_tga()` validates the 18-byte header, chooses the pixel reader and row expander, allocates either a one-row buffer or virtual array, skips the image ID, reads the colormap, and fills compressor metadata.

The code deliberately rejects interlaced TGA and unsupported colormap forms. It is format-conversion glue around libjpeg’s `cjpeg_source_struct`.
