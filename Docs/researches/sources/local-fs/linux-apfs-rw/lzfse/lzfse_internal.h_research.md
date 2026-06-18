# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse_internal.h

## Purpose
Defines internal LZFSE/LZVN constants, decoder state structures, block header layouts, utility functions, header validation, and L/M/D coding tables.

## Main Responsibilities
- Defines status codes, state counts, symbol counts, block magic constants, and maximum matches/literals per block.
- Defines decoder state for compressed LZFSE blocks, LZVN blocks, uncompressed blocks, and the overall stream.
- Defines on-stream block headers for uncompressed, LZFSE V1, LZFSE V2, and LZVN blocks.
- Provides unaligned-safe load/store/copy helpers.
- Provides bitfield `extract()` / `insert()` utilities.
- Validates compressed V1 headers and normalized frequency tables.
- Supplies L/M/D extra-bit and base-value tables.

## Key Types
- `lzfse_decoder_state`
- `lzfse_compressed_block_decoder_state`
- `lzfse_compressed_block_header_v1`
- `lzfse_compressed_block_header_v2`
- `lzvn_compressed_block_header`

## Dependencies
Includes `lzfse_fse.h` and Linux limits/stddef headers.

## Notes
`LZFSE_ENCODE_HASH_BITS` is referenced in a hash-values macro but encoding support is otherwise absent; the active decode path uses the decode-specific constants and tables.
