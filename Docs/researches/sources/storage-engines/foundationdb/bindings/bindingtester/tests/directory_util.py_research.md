# sources/storage-engines/foundationdb/bindings/bindingtester/tests/directory_util.py

## Purpose
`directory_util.py` provides shared helpers for bindingtester directory workloads: initial directory-layer setup, default-directory creation, prefix logging, duplicate-prefix validation, and high-contention allocator validation.

## Important APIs, Types, And Functions
- Constants: `DEFAULT_DIRECTORY_INDEX = 4`, `DEFAULT_DIRECTORY_PREFIX = b"default"`, and `DIRECTORY_ERROR_STRING = b"DIRECTORY_ERROR"`.
- `setup_directories(instructions, default_path, random)` resets `DirectoryStateTreeNode`, creates root subspaces/layers through instructions, creates a default directory subspace, sets the bindingtester error directory index, and returns the initial directory list.
- `create_default_directory_subspace()` forces a commit, switches to the generated layer, creates a database directory with a random `default-*` prefix, and restores directory index 4.
- `push_instruction_and_record_prefix()` emits a directory create/open instruction and records a packed key under the prefix log so later validation can detect duplicate allocations.
- `check_for_duplicate_prefixes(db, subspace)` scans recorded prefix keys in batches, filters default/error prefixes, and reports adjacent duplicate prefixes.
- `validate_hca_state(db)` inspects the directory layer's HCA counter/recent allocation subspaces and reports if actual recent allocations exceed the reported count.

## Control Flow
Setup creates two subspaces, wraps them into a directory layer, creates a default directory, and records that default in the state tree. Prefix recording optionally checks directory existence first, runs the target directory operation, switches to the new directory entry, packs a random key inside it, reorders stack values so existence and packed key become part of the tuple key, writes to the prefix log, and switches back to the default directory index.

## State And Persistence Behavior
The helper persists directory metadata, the default test directory, and prefix-log keys. Its validation functions read persistent test artifacts and internal HCA keys. Local state is mostly the returned `dir_list` plus the class-level `DirectoryStateTreeNode` model.

## Dependencies And Integration Points
This module depends on `fdb`, `struct`, bindingtester `util`, `test_util`, and `DirectoryStateTreeNode`. It is used by both `DirectoryTest` and `DirectoryHcaTest`, and its instruction names must match the bindingtester interpreter.

## Risks And Edge Cases
Duplicate detection assumes prefix-log keys sort by packed prefix and only compares adjacent prefixes across paged scans, so correct `last_prefix` handling is important. Prefixes with `DEFAULT_DIRECTORY_PREFIX` and `DIRECTORY_ERROR_STRING` are intentionally ignored. `validate_hca_state()` assumes current HCA layout under `fdb.Subspace((b"\xfe", b"hca"), b"\xfe")`; a directory-layer metadata layout change would require updates.

## Test Signals
Duplicate-prefix reports and HCA counter consistency are direct validation signals. The helpers also contribute setup correctness to every directory bindingtester workload.
