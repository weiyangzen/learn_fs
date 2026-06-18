# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/compress.c

This file provides a standalone LZJB compressor/decompressor and a simple 32-bit rolling checksum. It is compiled into the kernel, boot code, and savecore, so it avoids dependencies on external kernel symbols.

Core behavior:
- `compress()` implements LZJB, a derivative of LZRW1, using 3-byte minimum matches, 6 bits of encoded match length, 10 bits of offset, 256 uninitialized Lempel hash entries, and an 8-item copy bitmap.
- If compression output approaches the original size, `compress()` falls back to copying the original input and returns `s_len`.
- The compressor never intentionally reads past input or writes past an output buffer of original input size.
- `decompress()` copies input directly when compressed length is greater than or equal to destination length, otherwise decodes bitmap-controlled literal/copy items until input or destination ends.
- Copy items use overlapping forward byte copying, matching LZ-style back-reference semantics.
- Corrupt compressed data with an offset before the destination start returns the number of bytes decompressed so far.
- `checksum32()` rotates the accumulated 32-bit sum right by one bit and adds each byte.

Important invariants:
- The Lempel table is intentionally uninitialized, making `compress()` non-deterministic but faster and stack-local/MT-safe.
- `MATCH_MAX` is 66 bytes and offset reach is 1 KiB.
- `decompress()` does not guarantee full output on corrupt or truncated input; callers must compare returned length with expected length.
