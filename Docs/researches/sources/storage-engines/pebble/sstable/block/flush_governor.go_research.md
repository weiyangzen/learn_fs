## sources/storage-engines/pebble/sstable/block/flush_governor.go

Purpose: Decides when block writers should flush the current logical block before adding another KV, balancing target block size with allocator size-class fragmentation.

Important APIs/types/functions: `FlushGovernor`, `AllocationOverheadAllowance`, `MakeFlushGovernor`, `LowWatermark`, `ShouldFlush`, `String`, and `findClosestClass`.

Control flow: Without size classes, the governor sets low watermark to `targetBlockSize*blockSizeThreshold/100` rounded up and high/target boundary to the target size. With size classes, it adds `AllocationOverheadAllowance`, finds the closest allocator class, falls back to no-size-class mode if the target is outside useful class bounds, then sets target boundary to the closest class minus overhead and high watermark to the next class minus overhead. `ShouldFlush` never flushes if the block would not grow or if `sizeBefore` is below low watermark; it always flushes if `sizeAfter` exceeds high watermark; between target boundary and high watermark, it chooses the side with less wasted space.

State and persistence behavior: The governor is immutable and copied by value. It affects block boundaries and thus SSTable layout, index entries, cache allocation behavior, and block-property granularity, but has no serialized fields.

Dependencies and integration points: Depends on `internal/cache` metadata size, block `MetadataSize`, and sorted allocator size classes such as `sstable.JemallocSizeClasses`. Used by row/column block writers.

Risks: Size classes must be sorted for binary search. Constants assert slack and alignment; changes to cache/block metadata sizes can break compile-time checks. Thresholds near 100 are clamped to avoid low watermark exceeding target boundary.

Test signals: `flush_governor_internal_test.go` covers class selection, and `flush_governor_test.go` datadriven tests cover initialization and `ShouldFlush` behavior with custom and jemalloc classes.
