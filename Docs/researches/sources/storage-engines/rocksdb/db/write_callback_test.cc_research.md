# sources/storage-engines/rocksdb/db/write_callback_test.cc

Purpose: This file tests RocksDB write callbacks and user write callbacks across many write-thread configurations. It verifies that internal callbacks can accept or reject writes, influence batching, and coexist with public enqueue/WAL-finish notifications.

Important APIs/types/functions: Test fixtures define `WriteCallbackTestWriteCallback1`, `WriteCallbackTestWriteCallback2`, `MockWriteCallback`, and `MockUserWriteCallback`. `WriteCallbackPTest` parameterizes unordered writes, sequence-per-batch, two write queues, concurrent memtable writes, callback batching permission, WAL enablement, and pipelined writes.

Control flow: The parameterized test builds scenarios of successful/failing write operations, opens `DBImpl` with matching options, uses sync points inside `WriteThread::JoinBatchGroup` to inspect leader/follower states, launches multiple writer threads, and verifies callback status, user callback notifications, persisted keys, and visible sequence numbers. Unsupported option combinations are skipped. A simpler fixture test checks plain `DB::Write`, successful `WriteWithCallback`, failing `WriteWithCallback`, and public `DB::WriteWithCallback` using `UserWriteCallback`.

State and persistence behavior: Successful callback writes persist their batched keys and advance visible sequence numbers; failing callbacks return `Busy`, do not persist keys, and do not fire WAL-finish notifications. `OnWriteEnqueued` fires after the writer is linked/enqueued. `OnWalWriteFinish` fires only when WAL is enabled and the write succeeds.

Dependencies and integration points: The file depends on `db/write_callback.h`, `DBImpl`, `WriteThread` sync points, public `rocksdb/db.h`, `rocksdb/user_write_callback.h`, write batches, threading, random data generation, and per-thread DB paths.

Risks: The parameterized matrix is concurrency-sensitive and uses busy waits plus sync points to force ordering. Adding write-thread states or unsupported option combinations requires test updates. The test invokes callbacks with `nullptr` inside sync-point verification to infer success/failure, so mock callbacks must tolerate null DBs.

Test signals: Strong signals cover write-group leadership, no-batching mode, pipelined/two-queue exclusions, WAL vs no-WAL user callback timing, callback failure abort, key visibility, and sequence accounting.
