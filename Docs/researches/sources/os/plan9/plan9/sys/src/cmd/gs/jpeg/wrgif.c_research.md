# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/wrgif.c

IJG `djpeg` destination adapter for GIF output, compiled only under `GIF_SUPPORTED`.

Important design point:

- The file intentionally writes “uncompressed GIF” data to avoid LZW patent concerns in the original era. It emits each pixel as a code and periodically emits clear codes before the code width would grow.

Key functions:

- `flush_packet()`, `CHAR_OUT`, and `output()` pack variable-width GIF codes into GIF data sub-blocks.
- `compress_init()`, `compress_pixel()`, and `compress_term()` implement the pseudo-compressor state machine.
- `emit_header()` writes a GIF87a header, logical screen descriptor, global color table, image descriptor, initial code size, and starts pseudo-compression.
- `start_output_gif()` emits the header using the decompressor colormap or a synthesized 256-entry grayscale map.
- `put_pixel_rows()` writes one row of palette indexes.
- `finish_output_gif()` terminates the pseudo-compressed stream, writes the GIF block terminator and trailer, and checks write errors.
- `jinit_write_gif()` validates grayscale/RGB output, forces quantization for color or >8-bit input, caps desired colors at 256, verifies single-component output, and allocates the row buffer.

This is a command-line image-output adapter and does not interact with filesystem internals beyond writing the output stream.
