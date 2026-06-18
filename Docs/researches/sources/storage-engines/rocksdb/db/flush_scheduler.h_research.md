# sources/storage-engines/rocksdb/db/flush_scheduler.h

Declares `FlushScheduler`, the pending-flush column-family queue. The comments define the concurrency contract: methods generally require the DB mutex or single-threaded recovery context, while `ScheduleWork()` may be called concurrently with itself and `Empty()` may race with scheduling with reduced precision.

The public API is `ScheduleWork()`, `TakeNextColumnFamily()`, `Empty()`, and `Clear()`. `TakeNextColumnFamily()` returns a Ref'ed `ColumnFamilyData*`, and the caller must eventually unref it. The private `Node` contains a column-family pointer and next pointer. `head_` is an `std::atomic<Node*>`; debug builds also maintain `checking_set_` under `checking_mutex_` to catch duplicate scheduling and state mismatches.

The state model is a minimal stack. A scheduled CF is pushed with an extra ref. A consumer pops nodes until it finds a live CF or reaches empty. `Clear()` uses the same path to release all pending refs. No persisted state is involved.

Dependencies are just `ColumnFamilyData` by forward declaration and standard atomics/debug containers. Integration is with RocksDB DB flush scheduling, recovery, and cleanup code.

Risks are mostly API discipline: ownership is not encoded in RAII, the concurrency contract is narrow, and duplicate detection is debug-only. Test coverage is indirect through callers that depend on stable refs and one-time delivery of scheduled CFs.
