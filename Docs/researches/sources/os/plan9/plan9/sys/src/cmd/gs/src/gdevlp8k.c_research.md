# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevlp8k.c

Implements the Epson LP-8000 `lp8000` printer device using ESC/PAGE-style control sequences at 300 DPI. The long file comment documents the reverse-engineered printer data format, including simple and compressed modes.

The actual implementation only supports compressed data. `lp8000_print_page` allocates two scanline-sized buffers, writes a long fixed initialization sequence, skips blank lines, trims leading/trailing zero bytes, compresses repeated bytes, and emits each non-empty line with X/Y coordinate commands and compressed raster payload.

Compression rule: a repeated byte sequence is encoded as byte, byte, count-minus-two, split into chunks when the run exceeds 257 bytes. Non-repeated bytes are copied literally.

The driver applies fixed margins and a printer coordinate offset of 60 pixels. It recalculates X only when leading zero trimming changes the starting coordinate.

The file is very protocol-specific and hard-codes A4-oriented initialization and clipping values. It returns VM errors on buffer allocation failure and flushes/frees buffers on normal completion.
