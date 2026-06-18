# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_unsup.c

## Purpose
Provides placeholder implementations for block-manager operations that either do not apply to disaggregated storage yet or are intentionally no-ops. This keeps the `WT_BM` vtable complete while avoiding local-file semantics such as mmap, salvage, sync, and traditional verify.

## Important APIs, types, and functions
The file defines no-op or fixed-return implementations for checkpoint start/unload, compaction start/skip/page-skip/end, mapping queries/discard, salvage start/next/valid/end, sync, verify start/address/end, and `__wti_block_disagg_is_mapped`.

## Control flow
Every function consumes the standard `WT_BM` arguments with `WT_UNUSED` and returns success, except `__wti_block_disagg_is_mapped`, which returns false. The compaction skip/page-skip functions do not set `*skipp`, so the caller must not depend on these stubs for meaningful compaction decisions unless initialized elsewhere.

## State and persistence behavior
No persistent state is read or written. The behavior advertises that disaggregated storage does not currently use memory mapping, local-file syncing, local salvage iteration, or traditional block verification through these paths.

## Dependencies and integration points
These functions are installed into `WT_BM` by `block_disagg_mgr.c`. They satisfy generic block-manager API expectations while most real work is delegated to page-log reads, writes, checkpoint packing, metadata, and discard.

## Risks and edge cases
- Silent success can hide unsupported behavior if generic callers assume the operation had an effect.
- Compaction and verify paths may report success without validating or moving any remote blocks.
- Future callers that require initialized out-parameters must update these stubs; several currently ignore pointer outputs.
- The functions are appropriate only if higher layers explicitly understand disaggregated storage limitations.

## Test signals
Tests should verify that unsupported operations do not crash, that mapped-state queries return false, that generic APIs using these hooks preserve expected user-visible semantics, and that compaction/verify/salvage tests either skip disaggregated storage or assert the documented no-op behavior.
