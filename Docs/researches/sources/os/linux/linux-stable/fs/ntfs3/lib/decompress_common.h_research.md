# File Research: sources/os/linux/linux-stable/fs/ntfs3/lib/decompress_common.h

## Role

Shared inline utilities for LZX and XPRESS decompression: endian-safe unaligned access, little-endian bitstream reading, Huffman symbol decoding, and LZ77 match copying.

## Key Definitions and Helpers

- `forceinline` maps to `__always_inline`.
- `FAST_UNALIGNED_ACCESS` is enabled for x86 and ARM configurations that can benefit from word-copy match copying.
- `copy_unaligned_word()` copies one machine word through kernel unaligned helpers.
- `repeat_byte()` expands one byte to a machine-word-sized repeated pattern.
- `struct input_bitstream` tracks buffered bits, remaining bit count, and input byte pointers.
- `init_input_bitstream()` initializes a bitstream over an input buffer.
- `bitstream_ensure_bits()`, `bitstream_peek_bits()`, `bitstream_remove_bits()`, `bitstream_pop_bits()`, and `bitstream_read_bits()` manage high-to-low bit consumption from little-endian 16-bit coding units.
- `bitstream_read_byte()`, `bitstream_read_u16()`, `bitstream_read_u32()`, and `bitstream_read_bytes()` read literal interleaved data.
- `bitstream_align()` resets the buffered bit state.
- `read_huffsym()` decodes a Huffman symbol using the table produced by `make_huffman_decode_table()`.
- `lz_copy()` copies validated LZ77 matches, using word-at-a-time fast paths for non-overlapping matches and offset-1 run-length cases when available.

## Research Notes

The header deliberately keeps decompressor hot paths inline. Bounds validation is expected before `lz_copy()` is called; this lets the helper optimize copying without rechecking match validity.
