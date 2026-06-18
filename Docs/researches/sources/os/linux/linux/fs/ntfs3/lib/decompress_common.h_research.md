# File Research: sources/os/linux/linux/fs/ntfs3/lib/decompress_common.h

## Role

Shared header for XPRESS and LZX decompression. It defines bitstream primitives, Huffman symbol decoding, unaligned-copy optimizations, and LZ77 match copying.

## Key Definitions

- `forceinline` maps to `__always_inline`.
- `FAST_UNALIGNED_ACCESS` is enabled on x86 and ARM configurations with unaligned support.
- `WORDBYTES` reflects `sizeof(size_t)`.
- `struct input_bitstream` tracks:
  - left-justified bit buffer;
  - number of bits held;
  - next input byte;
  - end pointer.

## Bitstream Helpers

- `init_input_bitstream()` initializes stream state.
- `bitstream_ensure_bits()` loads little-endian 16-bit coding units into the bit buffer.
- `bitstream_peek_bits()`, `bitstream_remove_bits()`, `bitstream_pop_bits()`, and `bitstream_read_bits()` expose bit-level reading.
- `bitstream_read_byte()`, `bitstream_read_u16()`, `bitstream_read_u32()`, and `bitstream_read_bytes()` read literal embedded data.
- `bitstream_align()` discards buffered bits.

## Huffman and LZ Helpers

- Declares `make_huffman_decode_table()`.
- `read_huffsym()` decodes one symbol using the direct table fast path or binary-tree slow path.
- `lz_copy()` copies an already-validated LZ77 match from `dst - offset` to `dst`, with optimized word-at-a-time copies for unaligned-capable architectures and a bytewise fallback.

## Dependencies

Uses Linux string, compiler, type, slab, and unaligned-access headers.

## Research Notes

Callers are responsible for validating match length/offset and output bounds before calling `lz_copy()`. Input exhaustion behavior is deliberately permissive for bit decoding, where missing bits are effectively zero, while byte-array reads can fail via `NULL`.
