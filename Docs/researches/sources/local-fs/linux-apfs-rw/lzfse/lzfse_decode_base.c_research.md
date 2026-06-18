# File Research: sources/local-fs/linux-apfs-rw/lzfse/lzfse_decode_base.c

## Purpose
Contains the core LZFSE stream decoder, including compressed header decoding, FSE literal decoding, L/M/D match execution, uncompressed blocks, and LZVN sub-block dispatch.

## Main Responsibilities
- Decodes V2 compressed headers into V1 header form with packed bitfield extraction and compressed frequency-table decoding.
- Validates V1 block headers through `lzfse_check_block_header_v1()`.
- Builds FSE decoder tables for literal, literal-length, match-length, and distance streams.
- Decodes literal streams and L/M/D triplets using backward FSE bitstreams.
- Emits literals and back-referenced matches into the destination buffer, preserving state when the destination fills mid-symbol.
- Handles LZFSE stream block magic values for end-of-stream, uncompressed, LZFSE V1/V2, and LZVN blocks.

## Key Functions
- `lzfse_decode_v1_freq_value()`: decodes compact frequency-table values.
- `lzfse_decode_v1()`: expands a V2 header into a V1 header.
- `lzfse_decode_lmd()`: executes FSE-decoded literal/match/distance records.
- `lzfse_decode()`: top-level internal decoder state machine.

## Dependencies
Uses `lzfse_internal.h`, `lzfse_fse.c/.h` table initialization and bitstream helpers, and `lzvn_decode_base.h` for LZVN block decoding.

## Notes
The decoder requires full encoded block payloads to be available in source while allowing partial destination progress. It performs explicit distance, block-size, header-size, and frequency sanity checks before emitting data.
