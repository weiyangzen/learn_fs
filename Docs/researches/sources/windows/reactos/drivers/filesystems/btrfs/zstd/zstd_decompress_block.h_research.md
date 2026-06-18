# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_decompress_block.h

## Summary
Declares internal compressed-block decompression helpers.

## Key APIs
- `ZSTD_decompressBlock_internal()`.
- `ZSTD_buildFSETable()`.

## Important Behavior
The header notes that public `ZSTD_decompressBlock()` is already declared in `zstd.h`, while block-size and sequence-header helpers are declared through `zstd_internal.h`. Its two declarations are for decompression modules that need direct compressed-block execution and FSE decode-table generation.

## Risks
`ZSTD_buildFSETable()` is explicitly internal and assumes validated parameters, sufficient table storage, and normalized counts that sum correctly. It is not defensive as a standalone public API.
