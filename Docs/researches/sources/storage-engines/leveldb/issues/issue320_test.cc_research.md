# sources/storage-engines/leveldb/issues/issue320_test.cc

Purpose: stress regression for issue 320 involving many random writes, deletes, updates, large values, and retained snapshots.

Important APIs and functions: helpers `GenerateRandomNumber`, `CreateRandomString`, and test `Issue320.Test`.

Control flow: maintains an in-memory model vector of up to 10,000 key/value pairs, runs 200,000 random operations, checks existing values with `Get` before mutation, writes batches containing put/delete operations, and randomly replaces retained snapshots.

State and persistence behavior: exercises WAL/memtable/table/compaction behavior under snapshot retention, which can delay obsolete-file and obsolete-entry cleanup. Values are 1 KiB strings with deterministic index-derived prefixes.

Dependencies and integration: uses public `DB`, `WriteBatch`, snapshots, read/write options, and destroy/open helpers.

Risks and edge cases: random seed is fixed with `std::srand(0)`, giving reproducible coverage but not exhaustive exploration. Snapshot vector entries must all be released before DB close.

Test signals: strong long-run signal for consistency under snapshots and compaction pressure.
