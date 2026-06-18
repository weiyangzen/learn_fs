# sources/storage-engines/foundationdb/bindings/bindingtester/tests/api.py

## Purpose
This concrete bindingtester test generates randomized FoundationDB API instruction streams to compare binding behavior across languages. It covers transactions, reads, ranges, mutations, atomic operations, version APIs, tuple operations, conflict ranges, transaction sizing, storage metrics, and versionstamps.

## Important APIs, Types, And Functions
Top-level helpers `matches_op` and `is_non_transaction_op` classify operation variants. `ApiTest` extends `Test`, creates workspace/scratch/stack subspaces, and implements `setup`, stack-depth helpers, key/value generation, database preload, outstanding read waiting, `generate`, `check_versionstamps`, `validate`, and `get_result_specifications`.

## Control Flow
Generation starts with a transaction, read version, and preloaded database. It then randomly selects operations for `args.num_ops`, ensuring required stack types exist before appending instructions. Single-threaded database mutations/read variants wait for futures to keep stack and transactional state coherent. Versionstamp operations write expected correlated keys/values for later validation. Finalization waits for reads, commits, starts a new transaction, logs the stack, and commits again.

## State And Persistence Behavior
Generated instructions mutate a FoundationDB workspace subspace and scratch subspaces for versionstamp validation. The generator tracks stack size, string/key depth, outstanding async reads, generated keys, and capability flags such as `can_set_version`, `can_get_commit_version`, and `can_use_key_selectors`.

## Dependencies And Integration Points
It integrates with `test_util.RandomGenerator`, stack manipulation helpers, FoundationDB tuple/versionstamp APIs, tester instruction interpreters in each language, and `ResultSpecification` comparison with permissible global error filters 1007, 1009, and 1021.

## Risks And Edge Cases
The generator must maintain stack-depth bookkeeping exactly; mismatches become tester failures rather than Python errors. It disables some operations after versionstamp use because key selectors cannot be used safely. Database operations in concurrent mode avoid some non-idempotent atomic choices. Storage metric operations use fixed chunk sizes and randomized non-identical ranges.

## Test Signals
Bindingtester result comparisons over workspace and stack subspaces, plus `validate` versionstamp checks, reveal cross-binding semantic drift or instruction interpreter bugs.
