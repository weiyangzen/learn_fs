# sources/storage-engines/wiredtiger/src/include/block_inline.h

## Purpose
This header provides small inline block-manager helpers. It defines latency histogram increment functions, packing/unpacking helpers for extent-list pairs, endian conversion helpers for block headers, and a predicate for sweeping block handles.

## Important APIs, Types, And Functions
`WT_STAT_MSECS_HIST_INCR_FUNC` and `WT_STAT_USECS_HIST_INCR_FUNC` instantiate histogram helpers for normal and disaggregated block-manager read/write latency. `__wt_extlist_write_pair` and `__wt_extlist_read_pair` encode/decode extent offset and size as variable-length packed integers. `__wt_block_header_byteswap_copy` and `__wt_block_header_byteswap` convert `WT_BLOCK_HEADER` fields on big-endian systems. `__wt_block_header` returns `WT_BLOCK_HEADER_SIZE`. `__wt_block_eligible_for_sweep` says a block handle can be swept when it is local and its object id is at or below `bm->max_flushed_objectid`.

## Control Flow
Extent serialization writes offset first and size second; reading mirrors that order and casts unpacked `uint64_t` values to `wt_off_t`. Byteswap helpers copy before swapping when source and target differ. Sweep eligibility deliberately omits the active read-count check because callers perform that elsewhere.

## State And Persistence Behavior
The packing helpers participate in persistent checkpoint extent-list encoding. Header byteswapping preserves the on-disk little-endian format across host endian variants. Sweep eligibility affects lifecycle of block handles after object switching or flushing but does not itself close or free handles.

## Dependencies And Integration Points
The file depends on `block.h` structures, integer packing helpers, stats macros, endian helpers, and block-manager object-id state. It is used by block allocation/checkpoint code, read/write statistics, and multi-object sweeping paths.

## Risks
Encoding order must remain consistent with checkpoint readers. Endian conversion must only swap fields that are part of the fixed header and must preserve flags/padding. Sweep eligibility is only safe when combined with the separate read-reference check; using it alone could remove a handle still in use.

## Test Signals
Test extent pair encode/decode round trips, big-endian header conversion through simulated or platform tests, histogram updates for block IO, and object sweep behavior with remote blocks, old local blocks, and blocks newer than `max_flushed_objectid`.
