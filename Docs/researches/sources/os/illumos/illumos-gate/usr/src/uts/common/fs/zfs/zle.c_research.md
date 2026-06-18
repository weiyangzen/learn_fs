# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zle.c

## Purpose

`zle.c` implements ZFS zero-length encoding, a simple compression algorithm optimized for runs of zero bytes.

## Compression Format

Each compressed chunk begins with a length byte `b`.

- If `b < n`, the next `b + 1` bytes are literal data.
- If `b >= n`, the chunk represents `256 - b + 1` zero bytes.

The compression parameter `n` comes from the compression table. In `zio_compress.c`, ZLE uses level `64`.

## Functions

`zle_compress()` scans the source and emits either zero-run descriptors or literal-run descriptors.

For zero runs:

- It can encode up to `256 - n` zero bytes in one chunk.
- It emits only the length/control byte.

For literal runs:

- It can encode up to `n` literal bytes.
- It stops before a pair where both current and next byte are zero, allowing the next iteration to encode a zero run.
- It checks destination capacity before emitting a literal run.

If compression cannot consume all source bytes within the destination limit, it returns the original source length, signaling ineffective compression.

`zle_decompress()` reads chunk descriptors, copies literal bytes or emits zero bytes, and succeeds only if it exactly fills the destination buffer.

## Key Dependencies

- Used through `zio_compress_table[]` as the `zle` compressor/decompressor.
- Only depends on basic illumos types/macros.

## Notes for Future Readers

- This is not a general-purpose entropy compressor; it targets sparse/zero-heavy data.
- The compressor’s failure convention matches the ZIO compression layer: returning `s_len` means “store uncompressed.”
