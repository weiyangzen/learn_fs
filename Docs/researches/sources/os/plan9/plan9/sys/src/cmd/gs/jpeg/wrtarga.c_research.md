# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrtarga.c

IJG `djpeg` destination adapter for Targa/TGA output, compiled only under `TARGA_SUPPORTED`.

Supported outputs:

- Uncompressed top-down 8-bit grayscale.
- Uncompressed top-down 24-bit RGB stored as BGR bytes.
- 8-bit colormapped RGB with a 24-bit BGR palette when decompressor quantization is active.
- Quantized grayscale is demapped to grayscale samples because Targa has no mapped grayscale form in this writer.

Key functions:

- `write_header()` builds the 18-byte TGA header, selecting image type 1, 2, or 3 and marking the image top-down/non-interlaced.
- `put_pixel_rows()` converts RGB rows to BGR output.
- `put_gray_rows()` writes grayscale or palette-index rows directly.
- `put_demapped_gray()` maps quantized grayscale indexes back through the single-channel colormap.
- `start_output_tga()` writes the header, emits a BGR colormap when needed, and installs the final row writer.
- `jinit_write_targa()` calculates dimensions and allocates an I/O row buffer plus decompressor row buffer.

The writer assumes 8-bit samples and uses ordinary stdio output.
