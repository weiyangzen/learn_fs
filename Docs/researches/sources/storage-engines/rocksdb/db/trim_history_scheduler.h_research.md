# sources/storage-engines/rocksdb/db/trim_history_scheduler.h

## Purpose

`trim_history_scheduler.h` declares `TrimHistoryScheduler`, a thread-safe work queue for column families that may need flushed immutable memtable history trimming.

## Important APIs, Types, and Functions

The public API is `ScheduleWork(ColumnFamilyData*)`, `TakeNextColumnFamily()`, `Empty()`, and `Clear()`. The scheduler holds an atomic empty flag, an `autovector` of `ColumnFamilyData*`, and a mutex named `checking_mutex_`.

## Control Flow

Producers call `ScheduleWork` when a CF needs history trimming. Consumers call `TakeNextColumnFamily` and are responsible for invoking the trim operation and releasing the scheduler-held reference. `Empty` is a lightweight check suitable for avoiding unnecessary scheduler work, while `Clear` drains the queue during shutdown.

## State and Persistence Behavior

The scheduler state is memory-only. Its important persistence-adjacent effect is delaying or enabling removal of flushed memtable history, which can affect how much history remains available for reads, snapshots, or timestamp retention before later flush/compaction work.

## Dependencies and Integration Points

The header forward-declares `ColumnFamilyData` and depends on `autovector`, mutex, and atomic support. It integrates with DB background scheduling and memtable-list trimming.

## Risks and Test Signals

Risks include the stated FIFO contract diverging from vector back-pop implementation, unsafely interpreting relaxed `Empty` as a hard guarantee, and unclear ownership if callers do not know returned CFs are still referenced. Tests should check thread-safe draining, shutdown clear, duplicate entries, and dropped-CF cleanup.
