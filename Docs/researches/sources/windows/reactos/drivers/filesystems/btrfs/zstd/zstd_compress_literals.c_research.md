# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_literals.c

## Role

Implements literal-section compression for zstd blocks. It decides whether literals should be stored raw, represented as RLE, compressed with Huffman coding, or emitted using a repeated Huffman table.

## Main Functions

- `ZSTD_noCompressLiterals()`
  - Writes a raw literals section.
  - Chooses a 1, 2, or 3 byte literal header depending on source size.
  - Copies literal bytes directly after the header.
- `ZSTD_compressRleLiteralsBlock()`
  - Writes an RLE literals section.
  - Stores only the repeated byte after the header.
- `ZSTD_compressLiterals()`
  - Main literal compression selector.
  - Copies prior Huffman state into the next Huffman state before attempting reuse.
  - Skips compression when disabled or when literals are too small.
  - Uses `HUF_compress1X_repeat()` for single stream mode and `HUF_compress4X_repeat()` otherwise.
  - Falls back to raw literals if compression fails, is not beneficial, or produces an error.
  - Emits RLE literals if the Huffman compressor reports single-byte output.
  - Writes compressed literal headers for 3, 4, or 5 byte header formats.

## Key Policy

- Small literals are left uncompressed for speed unless a valid repeat table makes compression cheap enough to try.
- `ZSTD_minGain()` is used to reject compressed literals that do not save enough space.
- Fast strategy with literal compression disabled by policy will emit raw literals.
- Reused Huffman tables are marked with `set_repeat`; newly built tables leave the next table in check mode.

## Dependencies

- Includes `zstd_compress_literals.h`.
- Relies on internal zstd definitions from `zstd_compress_internal.h`.
- Calls Huffman APIs from the zstd HUF implementation through included internal headers.

## ReactOS/Btrfs Relevance

Btrfs zstd compression emits block payloads where literals often dominate compressed size. This file implements the literal-section decisions used by the block compressor in `zstd_compress.c`.

## Risks and Notes

- The function intentionally falls back to raw literals in many cases, prioritizing valid output and speed over marginal compression wins.
- Header size and compressed literal size are packed into bit fields; off-by-one changes would break zstd format compatibility.
- The function preserves prior Huffman state on fallback, which is important for entropy repeat semantics across blocks.
