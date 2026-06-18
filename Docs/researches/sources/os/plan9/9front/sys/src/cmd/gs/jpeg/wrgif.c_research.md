# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/wrgif.c

IJG `djpeg` output module for GIF. To avoid historical LZW patent exposure, it writes valid uncompressed GIF-style streams using literal symbols and periodic clear codes rather than implementing LZW compression.

Main data structures and entry points:
- `gif_dest_struct` extends `djpeg_dest_struct` with compressor backlink, variable-width code packing state, clear/EOF codes, symbol counter, and GIF packet buffer.
- `jinit_write_gif` validates output colorspace, forces quantization for RGB or >8-bit input, computes dimensions, verifies one output component, and allocates one output row.
- `start_output_gif` emits GIF header and global color table, using either the decompressor colormap or a generated grayscale map.
- `put_pixel_rows` sends each palette/grayscale index through `compress_pixel`.
- `finish_output_gif` writes EOF code, flushes packets, terminates image data and the GIF file.

Encoding details:
- `output` packs variable-width codes into bytes.
- `flush_packet` and `CHAR_OUT` produce GIF sub-blocks with count bytes.
- `compress_init`, `compress_pixel`, and `compress_term` implement the no-LZW pseudo-compression sequence.
- `emit_header` writes a GIF87a logical screen, global color table, image descriptor, and initial code size.

Important constraints:
- Maximum color count is 256.
- Non-grayscale RGB output must be quantized before GIF writing.
- Files are valid but larger than LZW-compressed GIFs.

Filesystem relevance:
- Sequential image-output adapter; no filesystem logic.
