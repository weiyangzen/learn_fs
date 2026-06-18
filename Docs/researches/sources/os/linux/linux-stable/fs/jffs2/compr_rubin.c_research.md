# File Research: sources/os/linux/linux-stable/fs/jffs2/compr_rubin.c

## Role

Implements the historical Rubin arithmetic-style compressors/decompressors used by JFFS2, including fixed MIPS probabilities and dynamic Rubin probabilities.

## Core Structures

- `struct pushpull` tracks bitstream buffer, bit offset, length, and reserved trailer space.
- `struct rubin_state` stores coding interval state (`p`, `q`, `rec_q`), bit counters, bit divider, per-bit probabilities, and the bitstream cursor.

## Encoding and Decoding

- `pushbit()` and `pullbit()` write/read single bits.
- `init_rubin()`, `encode()`, and `end_rubin()` implement the encoder state machine.
- `init_decode()`, `__do_decode()`, and `decode()` implement decoder reconstruction.
- `out_byte()` encodes one byte least-significant-bit first using per-bit probabilities.
- `in_byte()` decodes one byte with the same bit order.
- `rubin_do_compress()` writes encoded bytes and rejects output that is not smaller than input.
- `rubin_do_decompress()` reconstructs bytes until the requested output length is produced.

## Compressor Variants

- Rubin MIPS:
  - Uses `BIT_DIVIDER_MIPS` and `bits_mips`.
  - Compression function is compiled out.
  - Registered with decompression support.
- Dynamic Rubin:
  - Builds an input histogram.
  - Converts per-bit occurrence counts into 8 probability bytes stored at the start of compressed data.
  - Compresses with divider 256 and rejects non-beneficial output.

## Registration Details

The two compressor structs intentionally use historical on-flash compression IDs:

- `jffs2_rubinmips_comp` name `rubinmips`, compression ID `JFFS2_COMPR_DYNRUBIN`, no compression callback, decompression callback present.
- `jffs2_dynrubin_comp` name `dynrubin`, compression ID `JFFS2_COMPR_RUBINMIPS`, compression callback present but disabled by default, decompression callback present.

## Research Notes

This is compatibility code for older JFFS2 images. The header disables Rubin compressors for new compression, but decompression remains available so existing flash data can still be read.
