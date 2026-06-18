# sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory.py

## Purpose
`directory.py` defines `DirectoryTest`, a randomized bindingtester workload for the FoundationDB directory layer. It generates stack-machine instructions that exercise directory creation, opening, moving, removal, listing, subspace operations, directory partitions, database-level directory operations, and optional snapshot directory reads. The test is designed for cross-binding comparison: generated instructions run against each binding, then logged stack/directory/subspace outputs are compared.

## Important APIs, Types, And Functions
- `DirectoryTest(Test)` owns test subspaces: `stack_subspace`, `directory_log`, `subspace_log`, and `prefix_log`.
- `setup(args)` initializes `dir_index` and a `test_util.RandomGenerator` parameterized by max integer bits, API version, and enabled tuple types.
- `generate(args, thread_number)` is the core workload generator. It emits `InstructionSet` commands such as `NEW_TRANSACTION`, `DIRECTORY_CHANGE`, `DIRECTORY_CREATE`, `DIRECTORY_CREATE_OR_OPEN`, `DIRECTORY_MOVE`, `DIRECTORY_REMOVE`, `DIRECTORY_PACK_KEY`, `DIRECTORY_RANGE`, and `LOG_STACK`.
- `ensure_default_directory_subspace()` recreates and records the default directory subspace after destructive operations that may remove or move it.
- `generate_layer()` chooses directory layer bytes, including empty layer, `b"partition"`, `b"test_layer"`, or random bytes.
- `pre_run(db, args)` prepopulates several directories using Python's directory implementation to verify other bindings can interoperate with existing directory metadata.
- `get_result_specifications()` declares comparison rules over the stack, directory log, and subspace log, filtering common retry/conflict errors.
- Utility functions `generate_path()` and `generate_prefix()` produce intentionally small, collision-prone paths and prefixes, with special handling for partitions and single-threaded uniqueness.

## Control Flow
Generation starts by creating a transaction, bootstrapping standard directory layers through `directory_util.setup_directories()`, switching to the default directory, and predeclaring directories to be created in `pre_run`. For each random operation, the generator may switch the current directory index, computes the available operation set from the modeled directory state, chooses one operation, pushes arguments, appends an opcode, and updates the in-memory `DirectoryStateTreeNode` model. Some operations force blocking commits when single-threaded comparison would otherwise become nondeterministic due to high-contention prefix allocation. Finalization commits outstanding work, iterates every known directory entry to log directory/subspace metadata, logs the stack, and commits again.

## State And Persistence Behavior
The persistent database effects are directory-layer metadata, created/moved/removed directories, generated subspace keys, and log keys under the test subspace. The local state model is `self.dir_list`, `self.dir_index`, `self.root`, `self.prepopulated_dirs`, and the shared `DirectoryStateTreeNode` graph. Prefix allocation nondeterminism is mitigated by known-prefix tracking and by serial commits around selected database operations when `args.concurrency == 1`.

## Dependencies And Integration Points
This file depends on the Python `fdb` bindings, `bindingtester` base classes, `test_util`, `directory_util`, and `DirectoryStateTreeNode`. It integrates with the bindingtester stack interpreter through instruction names and with the comparison harness through `ResultSpecification`. It assumes directory layer semantics from `fdb.directory`.

## Risks And Edge Cases
The generated workload intentionally creates ambiguous outcomes: failed opens, moves of empty path, partition prefixes, unknown allocated prefixes, and default-directory fallback. The directory-state model is conservative, so false assumptions there could either skip useful operations or log entries that are not comparable. Duplicate prefix validation is disabled here because removed partitions can make later allocation collisions legitimate under this workload. API-version and concurrency constraints matter because older high-contention allocator behavior can be more deterministic-sensitive.

## Test Signals
Strong signals come from comparing the stack log, directory log, and subspace log across bindings, plus prepopulated directory compatibility. `global_error_filter=[1007,1009,1021]` tolerates expected transaction/retry errors. The disabled duplicate-prefix check documents a known limitation around partitions and removed directories.
