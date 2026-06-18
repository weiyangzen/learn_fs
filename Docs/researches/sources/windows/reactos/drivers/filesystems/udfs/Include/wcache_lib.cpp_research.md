# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/wcache_lib.cpp

## Purpose
Implements the UDFS write/read cache library for block media. It supports ROM, rewritable, write-once, and RAM-like modes, including packet-sized read/modify/write behavior, cache eviction, direct cached-block access, flush/purge, bad-block policy flags, and limited async/chained I/O support.

## Main Contents
- Initializes cache metadata and backing tables in `WCacheInit__`.
- Maintains sorted lists of cached blocks, modified blocks, and cached frames.
- Uses frame-based cache organization where each frame contains per-block cache entries.
- Implements random/heuristic eviction through `WCacheFindLbaToRelease`, `WCacheFindModifiedLbaToRelease`, and `WCacheFindFrameToRelease`.
- Implements sorted-list helpers:
  - `WCacheGetSortedListIndex`
  - `WCacheInsertRangeToList`
  - `WCacheInsertItemToList`
  - `WCacheRemoveRangeFromList`
  - `WCacheRemoveItemFromList`
- Allocates/removes cache frames through `WCacheInitFrame` and `WCacheRemoveFrame`.
- Encodes modified flags in low pointer bits through `WCacheSetModFlag`, `WCacheClrModFlag`, `WCacheGetModFlag`, and `WCacheSectorAddr`.
- Implements packet update/writeback through `WCacheUpdatePacket` and `WCacheUpdatePacketComplete`.
- Enforces limits with mode-specific implementations:
  - `WCacheCheckLimitsRW`
  - `WCacheCheckLimitsRAM`
  - `WCacheCheckLimitsR`
- Implements read path in `WCacheReadBlocks__`, including direct large reads and caching newly read sectors.
- Implements write path in `WCacheWriteBlocks__`, including write-through optimization for aligned writes and modified-list tracking.
- Implements full flush/purge:
  - `WCacheFlushAll__`
  - `WCachePurgeAll__`
  - `WCacheFlushAllRW`
  - `WCachePurgeAllRW`
  - `WCacheFlushAllRAM`
  - `WCachePurgeAllRAM`
  - `WCachePurgeAllR`
- Implements range flush in `WCacheFlushBlocks__` and `WCacheFlushBlocksRW`.
- Implements direct cache access through `WCacheStartDirect__`, `WCacheDirect__`, `WCacheEODirect__`, and `WCacheIsCached__`.
- Implements WORM relocation-table synchronization through `WCacheSyncReloc__`.
- Implements cache discard through `WCacheDiscardBlocks__`.
- Implements async completion callback `WCacheCompleteAsync__`.
- Parses and mutates cache flags through `WCacheDecodeFlags` and `WCacheChFlags__`.

## Dependencies and Interactions
- Depends on callback APIs declared in `wcache_lib.h`: physical read/write, async read/write, block-used checks, relocation updates, and error handling.
- Uses kernel synchronization via `ERESOURCE` and resource acquire/release calls.
- Uses UDFS allocation/debug wrappers such as `MyAllocatePoolTag__`, `MyFreePool__`, `DbgAllocatePoolWithTag`, `DbgFreePool`, `DbgCopyMemory`, and `DbgMoveMemory`.
- Relies on caller-supplied `CheckUsedProc` to distinguish used, zero, and bad blocks.
- Relies on `UpdateRelocProc` for write-once media relocation behavior.

## Notable Details
- Async support exists structurally but comments say it is not completely implemented; initialization disables async write for WORM mode.
- Cache entries store flags in low pointer bits, requiring alignment assumptions and `WCACHE_ADDR_MASK`.
- `WCacheRelease__` frees many internal allocations, but its checks for `tmp_buff` and `reloc_tab` use `Cache->CachedFramesList` rather than the specific pointer fields.
- `WCacheDiscardBlocks__` loops using `while((List[i] < end) && (i < Cache->BlockCount))`, evaluating `List[i]` before checking bounds.
- The RAM path flushes contiguous modified sectors directly, while RW/ROM paths use packet update semantics.
- WORM mode packs modified blocks into relocation packets and writes through `WriteProc` with `NULL` LBA, relying on callback semantics.
