# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress.c

## Role

Main Zstandard compression implementation vendored into the ReactOS Btrfs filesystem driver. It implements compression contexts, parameter handling, dictionary support, block/frame compression, streaming compression, and compression level presets.

## Major Responsibilities

- Provides public and internal compression entry points:
  - `ZSTD_compress()`, `ZSTD_compressCCtx()`, `ZSTD_compress2()`
  - `ZSTD_compressBegin*()`, `ZSTD_compressContinue()`, `ZSTD_compressEnd()`
  - `ZSTD_compressStream*()`, `ZSTD_flushStream()`, `ZSTD_endStream()`
- Manages `ZSTD_CCtx`, `ZSTD_CStream`, and `ZSTD_CDict` allocation, reset, sizing, and freeing.
- Converts user-facing compression levels and advanced parameters into validated `ZSTD_compressionParameters`.
- Builds and maintains per-block match state, entropy state, literal buffers, sequence buffers, and streaming input/output buffers.
- Handles dictionary modes:
  - raw dictionary content
  - full zstd dictionary with entropy tables
  - copied CDict tables
  - attached dictionary match state
  - prefix dictionary
- Encodes full zstd frames:
  - frame header
  - compressed/raw/RLE blocks
  - optional checksum
  - final empty block when required

## Compression Flow

The central one-shot path is:

1. Initialize or reset a `ZSTD_CCtx`.
2. Resolve requested parameters into applied parameters with `ZSTD_getCParamsFromCCtxParams()`.
3. Allocate workspace and block buffers in `ZSTD_resetCCtx_internal()`.
4. Optionally load dictionary content or attach/copy a `ZSTD_CDict`.
5. Write frame header in `ZSTD_writeFrameHeader()`.
6. Split input into blocks in `ZSTD_compress_frameChunk()`.
7. For each block:
   - update window state
   - correct index overflow if needed
   - validate dictionary distance
   - build sequence store with selected matcher
   - compress literals and sequences
   - fall back to raw/RLE block if compression is not beneficial
8. Write epilogue/checksum in `ZSTD_writeEpilogue()`.

## Important Internal Mechanics

- `ZSTD_resetCCtx_internal()` is the main workspace allocator and state initializer. It computes block size, token space, match table space, LDM space, streaming buffers, entropy workspace, and sequence buffers.
- `ZSTD_selectBlockCompressor()` dispatches match finding by strategy and dictionary mode:
  - fast
  - double fast
  - greedy
  - lazy/lazy2
  - btlazy2
  - btopt/btultra/btultra2
- `ZSTD_compressSequences_internal()` compresses the literal section, writes sequence count headers, selects/builds FSE tables for literal lengths, offsets, and match lengths, then calls `ZSTD_encodeSequences()`.
- `ZSTD_compressBlock_internal()` handles normal block compression and RLE optimization.
- `ZSTD_compressBlock_targetCBlockSize()` routes through superblock compression when target compressed block sizing is requested.
- `ZSTD_overflowCorrectIfNeeded()` rescales match table indices before 32-bit index overflow.
- `ZSTD_writeFrameHeader()` implements zstd frame descriptor construction, dictionary ID fields, window descriptor, content size fields, and magicless format support.

## Dictionary Handling

Dictionary support is extensive and safety-sensitive.

- `ZSTD_compress_insertDictionary()` chooses raw vs full dictionary handling based on `ZSTD_dictContentType_e` and dictionary magic.
- `ZSTD_loadZstdDictionary()` parses full zstd dictionaries:
  - dictionary ID
  - HUF table
  - FSE offset/match-length/literal-length tables
  - repeat offsets
  - dictionary content
- `ZSTD_checkDictNCount()` rejects dictionaries whose normalized FSE distributions cannot encode required symbols.
- `ZSTD_shouldAttachDict()` decides whether to reference CDict match tables or copy them into the active context.
- Attached dictionaries are invalidated when the active input advances beyond the configured window.

## Streaming Behavior

`ZSTD_compressStream2()` provides transparent initialization. When the stream is still in `zcss_init`, it resolves parameters, initializes local dictionaries, and creates either a single-threaded stream state or, under `ZSTD_MULTITHREAD`, delegates to `ZSTDMT`.

Single-threaded streaming uses these stages:

- `zcss_load`: load input into the context input buffer or directly compress final input if output capacity is large enough.
- `zcss_flush`: flush compressed output from the internal output buffer.
- `zcss_init`: requires initialization before compression.

The stream resets session state when a frame ends.

## ReactOS/Btrfs Relevance

This file is compression-library code embedded under the ReactOS Btrfs driver. The filesystem-facing value is the availability of zstd frame/block compression for Btrfs compressed extents. The code itself is generic zstd compression logic, not Btrfs metadata logic.

## Risks and Notes

- This is vendored third-party code with broad API surface; local modifications should be minimized unless syncing with upstream zstd.
- External sequence support explicitly warns that sequences are not verified and invalid sequences may cause out-of-bounds access or data corruption.
- Static contexts cannot resize; many APIs reject static contexts when allocation would be required.
- Dictionary lifetime matters for by-reference dictionaries and attached CDicts.
- Streaming APIs have legacy behavior where pledged source size `0` is treated as unknown in several compatibility paths.
