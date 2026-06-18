# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sdct.h

Header defining Ghostscript DCT/JPEG stream filter state.

Major contents:

- `jpeg_block_t`, used to track immovable allocations made for IJG JPEG library data.
- Common JPEG stream data containing a copied stream template, IJG error manager, `jmp_buf`, allocator, allocation block list, and `Picky`/`Relax` flags.
- `jpeg_compress_data`, wrapping `jpeg_compress_struct`, destination manager, and final-output buffer.
- `jpeg_decompress_data`, wrapping `jpeg_decompress_struct`, source manager, skip state, fake-EOI state, optional scanline buffer, and scanline byte count.
- `stream_DCT_state`, the GC-managed Ghostscript stream state containing marker data, `QFactor`, `ColorTransform`, `NoMarker`, JPEG memory, compress/decompress data pointer, scanline size, and processing phase.
- Public GC descriptor macros and declarations for `s_DCTD_template`, `s_DCTE_template`, and `s_DCT_set_defaults`.

This is JPEG/DCT stream state infrastructure, not filesystem code.
