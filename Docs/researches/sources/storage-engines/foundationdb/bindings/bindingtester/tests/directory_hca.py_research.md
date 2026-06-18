# sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_hca.py

## Purpose
`directory_hca.py` defines `DirectoryHcaTest`, a bindingtester workload focused on the directory layer's high-contention allocator (HCA). It creates many directories concurrently and validates that allocated prefixes are unique and that the HCA's internal counters remain consistent.

## Important APIs, Types, And Functions
- `DirectoryHcaTest(Test)` uses `coordination` keys for barriers and `prefix_log` for allocated-prefix evidence.
- `setup(args)` configures a `RandomGenerator`, three transaction names (`tr0`..`tr2`), barrier numbering, and maximum directories per transaction. It rejects `args.concurrency > 8` for API versions before 300.
- `commit_transactions()` randomly commits named transactions, forcing commits for older API versions.
- `barrier()` uses database instructions `SET_DATABASE`, `CLEAR_DATABASE`, and `WAIT_EMPTY` to synchronize concurrent bindingtester threads around HCA pressure phases.
- `generate(args, thread_number)` creates the default directory setup, then loops until `args.num_ops` directory create operations have been emitted.
- `pre_run(tr, args)` seeds the first barrier keys when concurrency is enabled.
- `validate(db, args)` calls `directory_util.check_for_duplicate_prefixes()` and `directory_util.validate_hca_state()`.

## Control Flow
After bootstrapping a default directory, each loop iteration optionally enters a barrier, switches to a random named transaction, emits one or more `DIRECTORY_CREATE` operations with random Unicode one-component paths and no explicit prefix, records allocated prefixes, optionally enters a second barrier, and lets thread zero commit transactions. Barriers arrange overlapping allocator pressure across worker threads while preserving enough ordering to know when all participants have reached a phase.

## State And Persistence Behavior
Persistent state includes created directories, prefix-log records, and coordination keys. Local state includes `transactions`, `barrier_num`, and `num_dirs`. The HCA state under the directory layer is not modified directly but is inspected in validation through its counters and recent allocation subspaces.

## Dependencies And Integration Points
This test depends on `directory_util.setup_directories()` and `push_instruction_and_record_prefix()` for directory setup and prefix logging. It relies on instruction semantics for named transactions and database-level waits, and uses `fdb.transactional` for pre-run coordination initialization.

## Risks And Edge Cases
The test is highly concurrency-sensitive. If barriers are misordered or named transactions are not isolated by a binding implementation, prefix collisions may be misattributed. Older API versions reduce the per-transaction directory count to avoid known HCA/concurrency limits. Thread zero receives a special one-directory path under concurrency to keep global progress/commit behavior controlled.

## Test Signals
The primary signals are absence of duplicate non-default prefixes in `prefix_log` and `validate_hca_state()` confirming the current HCA window's actual recent allocation count does not exceed its reported counter. Barrier completion also indirectly tests database wait/empty semantics.
