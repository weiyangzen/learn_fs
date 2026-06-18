# sources/storage-engines/rocksdb/memtable/write_buffer_manager_test.cc

## Purpose
`write_buffer_manager_test.cc` validates `WriteBufferManager` memory-pressure and cache-charging behavior.

## Important Tests and Helpers
- `WriteBufferManagerTest.ShouldFlush` checks active and total memory threshold behavior for a 10 MiB manager.
- `ChargeWriteBufferTest.Basic` verifies cache dummy-entry reservation growth and delayed shrink with a 50 MiB write-buffer limit.
- `BasicWithNoBufferSizeLimit` verifies cache charging when write-buffer size is zero, meaning no flush pressure limit but cache cost still applies.
- `BasicWithCacheFull` uses strict LRU cache capacity to verify partial reservation failures and recovery after capacity increases.
- `kSizeDummyEntry` defines the expected cache reservation quantum of 256 KiB.

## Control Flow
The flush test reserves, schedules, frees, and resizes memory while asserting `ShouldFlush()` transitions. It distinguishes total memory over hard limit from active mutable memory over mutable limit, including cases where enough memory is already being flushed.

Cache tests create LRU caches, reserve memory in increments, and compare `dummy_entries_in_cache_usage()` plus pinned cache usage against expected reservation quanta and metadata overhead bounds. They then free memory in large and small chunks to verify delayed decrease behavior. The full-cache test intentionally exceeds strict cache capacity, observes partial reservation, frees memory, increases capacity, and verifies subsequent reservations can fully succeed.

## State and Persistence Behavior
All state is test-local memory. Cache pinned usage reflects dummy write-buffer reservations and is expected to return to zero after manager destruction in the basic cache test.

## Dependencies and Integration Points
The file includes `rocksdb/write_buffer_manager.h`, `rocksdb/advanced_cache.h`, and the RocksDB test harness. It directly exercises public manager APIs and indirect `CacheReservationManager` behavior via cache usage observations.

## Risks and Test Signals
The tests provide strong coverage for accounting thresholds and cache charging but do not cover write-stall queue behavior. Assertions include metadata overhead tolerances because cache bookkeeping adds implementation-dependent bytes. The strict-capacity case documents that reservation failure is tolerated and later corrected as memory is freed or cache capacity increases.
