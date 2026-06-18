# sources/storage-engines/wiredtiger/src/include/connection.h

## Purpose
`connection.h` defines process-wide and connection-wide internal state for WiredTiger. It is the central header for connection lifecycle, subsystem registries, background server state, shared caches, extension lists, data-handle/block lists, backup, disaggregated/tiered storage, diagnostics, and connection flags.

## Important APIs, Types, and Functions
`WT_PROCESS` stores global library state: process spinlock, connection queue, checksum function pointers, timestamp conversion settings, shared cache pool, and a modify pad byte hook. `WT_CONNECTION_IMPL` is the main connection object embedding the public `WT_CONNECTION` interface and holding locks, home/config/version state, session array, data handles, block/file handles, cache/eviction/transaction/log/checkpoint subsystems, extension APIs, compiled configuration arrays, server flags, diagnostics, and filesystem/key-provider interfaces.

Important subsystem structs include `WT_BACKGROUND_COMPACT`, `WT_LAYERED_TABLE_MANAGER`, `WT_DISAGGREGATED_STORAGE`, `WT_PAGE_HISTORY`, `WT_CONN_EXTENSIONS`, `WT_CONN_BACKUP`, `WT_CONN_PREFETCH`, `WT_CONN_CAPACITY`, `WT_CONN_STAT_LOG`, `WT_CONN_SWEEP`, and `WT_CONN_TIERED`. Macros manage dhandle/block insertion/removal, panic checks, hot-backup start, incremental backup flags, bucket-storage context, and close-abort debugging.

## Control Flow
Connection open initializes global/process linkage, locks, extension registries, sessions, config entries, and selected server subsystems. Runtime code routes through `WT_CONNECTION_IMPL`: sessions locate shared cache/txn/log metadata; schema and handle code use the dhandle queues and hash tables; background servers use their embedded sessions, condition variables, and thread IDs; reconfigure updates connection fields under dedicated locks. Close/shutdown tears down server flags, handles, extensions, backup state, and free-on-close allocations.

## State and Persistence Behavior
Most fields are in-memory coordination state, but many mirror durable or externally visible state: compatibility/recovery versions, checkpoint/turtle metadata versions, backup timestamps/file lists, log manager state, disaggregated checkpoint metadata LSNs/checksums/timestamps, database size, pending encryption keys for checkpoint persistence, and metadata operation queues. Atomic/shared fields coordinate readers and server threads without broad locking.

## Dependencies and Integration Points
The header touches nearly every WiredTiger subsystem: sessions, cache, eviction, transaction, logging, checkpoint, rollback-to-stable, block cache, tiered and disaggregated storage, extensions, file systems, encryption/key providers, statistics, background compaction, prefetch, live restore, and generated config. It also depends heavily on queue macros, spin/rw locks, atomics, and flag-generation conventions.

## Risks and Edge Cases
This is high-blast-radius state. Risks include lock-order mistakes across schema/metadata/checkpoint/dhandle locks, stale atomic state during reconfigure or shutdown, incorrect queue/hash count maintenance, server-thread lifetime races, and mismatched durable metadata around disaggregated checkpoints or key rotation. Macros such as `WT_CONN_DHANDLE_INSERT/REMOVE` assume specific locks and a `session` name in scope. Flags are split between regular and atomic fields, so using the wrong accessor can race.

## Test Signals
Relevant tests include connection open/close/reconfigure, recovery/compatibility, backup and incremental backup, background compaction, tiered/disaggregated storage, extension registration/termination, cache/eviction stress, logging/checkpoint shutdown, and diagnostic stress/failpoint suites. Thread sanitizer and long-running concurrency tests are valuable for this header's invariants.
