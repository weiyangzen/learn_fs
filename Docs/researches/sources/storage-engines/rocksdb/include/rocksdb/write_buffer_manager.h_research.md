<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_buffer_manager.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/write_buffer_manager.h

Purpose: Declares `WriteBufferManager`, which coordinates memory accounting and optional write stalls across one or more DB instances' memtables. It can also charge memtable memory to a shared cache through dummy reservations.

Important APIs/types/functions: `StallInterface` exposes `Block` and `Signal` callbacks for DB instances. `WriteBufferManager` provides `enabled`, `cost_to_cache`, `memory_usage`, `mutable_memtable_memory_usage`, `dummy_entries_in_cache_usage`, `buffer_size`, `SetBufferSize`, `SetAllowStall`, `ShouldFlush`, `ShouldStall`, `IsStallActive`, `IsStallThresholdExceeded`, `ReserveMem`, `ScheduleFreeMem`, `FreeMem`, `BeginWriteStall`, `MaybeEndWriteStall`, and `RemoveDBFromQueue`.

Control flow: Memtable allocations call `ReserveMem`; pending frees can be moved out of active accounting by `ScheduleFreeMem` and finalized by `FreeMem`. Writers query `ShouldFlush` to trigger flushes when mutable or total memory crosses thresholds. If `allow_stall` is enabled and total usage exceeds the buffer size, DBs enter a queue and are blocked until `MaybeEndWriteStall` signals them.

State and persistence behavior: All state is in-memory: atomic buffer limits, memory-used counters, cache reservation manager, stall queue, mutexes, and stall-active flag. It affects flush timing and write admission, but does not persist data itself.

Dependencies and integration points: Depends on `Cache`, `CacheReservationManager`, atomics, mutexes, condition coordination through `StallInterface`, and internal DB write/flush scheduling. It integrates with shared cache memory budgets and multi-DB deployments.

Risks and edge cases: A zero buffer size disables enforcement and makes memory usage invalid for limiting decisions. Stall state combines lock-protected queue updates with atomic reads, so implementation must avoid lost signals. Charging to cache requires reservation/free paths to stay balanced.

Test signals: `WriteBufferManager` and memtable tests should verify flush thresholds, active versus scheduled-free memory, cache dummy usage, runtime buffer-size changes, stall begin/end signaling, DB queue removal, and disabled/allow-stall toggles.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/write_buffer_manager.h -->
