<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_repl_stress.cc -->
# sources/storage-engines/rocksdb/tools/db_repl_stress.cc

## Purpose
`db_repl_stress.cc` stress-tests RocksDB replication log iteration by writing random data on a background thread while the main thread continuously consumes updates through `DB::GetUpdatesSince()`. It verifies that transaction-log batches are observed in contiguous sequence-number order and that no extra or missing updates appear.

## Important APIs, Types, and Functions
- gflags: `--num_inserts`, `--wal_ttl_seconds`, and `--wal_size_limit_MB`.
- `DataPumpThread` carries an already-opened `DB*` to the writer thread.
- `DataPumpThreadBody()` writes `FLAGS_num_inserts` random 500-byte keys and values using `DB::Put()`.
- `main()` configures WAL retention options, creates a fresh DB, starts the writer thread with `Env::StartThread()`, and repeatedly opens `TransactionLogIterator` instances with `GetUpdatesSince(currentSeqNum, &iter)`.
- `BatchResult.sequence` is compared to the expected `currentSeqNum`.

## Control Flow
After parsing flags, the program builds a test DB path from `Env::GetTestDirectory()`, destroys any previous DB, opens a new DB, and starts the writer. The main loop repeatedly tries `GetUpdatesSince()`. If the API cannot provide an iterator, it probes until either enough updates have already been read or a new iterator becomes available. When the iterator is valid, it walks batches, incrementing both `num_read` and `currentSeqNum`. Success is declared after all expected inserts have been read and subsequent probing cannot find more updates.

## State and Persistence Behavior
The program writes a real RocksDB database and WAL files under the environment's test directory. WAL retention is governed by `WAL_ttl_seconds` and `WAL_size_limit_MB`. The DB is destroyed before opening but is not explicitly destroyed after success. Sequence state is in-memory only; the persistence behavior under test is WAL availability to transaction-log iteration.

## Dependencies and Integration Points
The file depends on gflags, `rocksdb/db.h`, transaction log iterator APIs, `db/write_batch_internal.h`, `test_util/testutil.h`, and RocksDB's `Env` thread launcher. Without gflags it builds a small `main()` that asks the user to install gflags and returns failure.

## Risks and Edge Cases
- The writer thread is not joined. The main thread exits once it has read all expected updates, relying on process termination for cleanup.
- Random keys can collide in theory, but sequence-number checks are independent of key uniqueness.
- WAL TTL or size settings that remove logs too aggressively can cause repeated `GetUpdatesSince()` failures before all updates are read.
- The program assumes one write batch per `Put()` and increments expected sequence by one per batch.

## Test Signals
The signal is process exit status and stderr messages. It prints "Successful!" and returns zero when exactly `num_inserts` ordered updates are observed; it exits nonzero on open failure, write failure, missed sequence numbers, or too many updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_repl_stress.cc -->
