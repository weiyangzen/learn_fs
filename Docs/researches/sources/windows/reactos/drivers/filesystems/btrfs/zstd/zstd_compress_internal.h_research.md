# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_compress_internal.h

## Role

Private compression header for zstd modules under `lib/compress`. It defines the core internal state structures, helper routines, match/window management primitives, sequence storage helpers, hashing functions, and private function prototypes used by the compression implementation files.

## Major Definitions

- Compression stages:
  - `ZSTDcs_created`
  - `ZSTDcs_init`
  - `ZSTDcs_ongoing`
  - `ZSTDcs_ending`
- Streaming stages:
  - `zcss_init`
  - `zcss_load`
  - `zcss_flush`
- Dictionary state:
  - `ZSTD_prefixDict`
  - `ZSTD_localDict`
  - `ZSTD_dictMode_e`
- Entropy state:
  - `ZSTD_hufCTables_t`
  - `ZSTD_fseCTables_t`
  - `ZSTD_entropyCTables_t`
  - `ZSTD_compressedBlockState_t`
- Match/window state:
  - `ZSTD_window_t`
  - `ZSTD_matchState_t`
  - `ZSTD_blockState_t`
- Long distance matching:
  - `ldmEntry_t`
  - `ldmState_t`
  - `ldmParams_t`
  - `rawSeq`
  - `rawSeqStore_t`
- Context parameter and runtime state:
  - `ZSTD_CCtx_params_s`
  - `ZSTD_CCtx_s`

## Important Helpers

- `ZSTD_LLcode()` and `ZSTD_MLcode()` map literal and match lengths to zstd entropy symbols.
- `ZSTD_updateRep()` updates repeat offsets after a sequence.
- `ZSTD_noCompressBlock()` writes raw block headers and payloads.
- `ZSTD_rleCompressBlock()` writes RLE block headers and one literal byte.
- `ZSTD_minGain()` computes the minimum gain required before compressed output is accepted.
- `ZSTD_disableLiteralsCompression()` implements literal-compression mode policy.
- `ZSTD_storeSeq()` copies literals and records one sequence in `seqStore_t`.
- `ZSTD_count()` and `ZSTD_count_2segments()` count match length in one or two memory segments.
- `ZSTD_hashPtr()` and related functions provide match hash functions for 4-8 byte match lengths.
- Rolling hash helpers support long distance matching.

## Window Management

The header contains the core rolling window logic used by all matchers:

- `ZSTD_window_init()` initializes a safe nonzero base/limit state.
- `ZSTD_window_update()` appends source ranges and switches non-contiguous prior input into external-dictionary mode.
- `ZSTD_window_clear()` drops prior match history.
- `ZSTD_window_hasExtDict()` detects external dictionary state.
- `ZSTD_matchState_dictMode()` chooses no-dict, ext-dict, or dict-match-state mode.
- `ZSTD_window_needOverflowCorrection()` and `ZSTD_window_correctOverflow()` protect 32-bit match indices from overflow.
- `ZSTD_window_enforceMaxDist()` enforces the maximum match distance and invalidates dictionaries when too far away.
- `ZSTD_checkDictValidity()` invalidates attached dictionaries for blocks beyond window range.
- `ZSTD_getLowestMatchIndex()` and `ZSTD_getLowestPrefixIndex()` compute match search lower bounds.

## Private API Surface

The header exposes private compression functions used across zstd compression modules:

- `ZSTD_selectBlockCompressor()`
- `ZSTD_loadCEntropy()`
- `ZSTD_reset_compressedBlockState()`
- `ZSTD_getCParamsFromCCtxParams()`
- `ZSTD_initCStream_internal()`
- `ZSTD_resetSeqStore()`
- `ZSTD_getCParamsFromCDict()`
- `ZSTD_compressBegin_advanced_internal()`
- `ZSTD_compress_advanced_internal()`
- `ZSTD_writeLastEmptyBlock()`
- `ZSTD_referenceExternalSequences()`
- `ZSTD_cycleLog()`

## ReactOS/Btrfs Relevance

This header is the structural backbone for the vendored zstd compressor. In the Btrfs driver context, it defines how compressed extent data is transformed into zstd frames/blocks and how compression memory is managed inside the driver’s zstd subsystem.

## Risks and Notes

- Most functions are `MEM_STATIC`/inline internal helpers, so behavioral changes here can affect every matcher and compressor path.
- `ZSTD_storeSeq()` assumes sequence store capacity and literal buffer limits were correctly allocated by the context reset path.
- Window/index correction logic is subtle and critical for long streams and reused contexts.
- Dictionary validity depends on correct maintenance of `loadedDictEnd`, `dictLimit`, and `lowLimit`.
