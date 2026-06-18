# sources/test-tools/crashmonkey/code/tests/generic_002.cpp

Purpose: CrashMonkey reproduction of xfstests generic/002. It exercises hard-link count durability while creating ten links to `foo` and then removing them, with a checkpoint after every fsync.

Important APIs/types/functions: `Generic002`, `link`, `remove`, `fsync`, `Checkpoint`, `stat`, `st_nlink`, `chmod`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: `setup()` creates `test_dir_a/foo` and syncs. `run()` loops over `foo_link_0` through `foo_link_9`, creates each hard link, fsyncs `foo`, checkpoints, then removes each link with another fsync and checkpoint. Return value 1 marks the final checkpoint.

State/persistence behavior: recovered `st_nlink` should match the number of links implied by `last_checkpoint`, allowing a one-operation delta because the crash may occur after fsync but before the user checkpoint record.

Dependencies/integration: uses `mnt_dir_` from `init_values`, raw POSIX hard-link operations, and CrashMonkey user checkpoints.

Risks/test signals: the oracle subtracts one link for the original file and uses checkpoint arithmetic; off-by-one errors in checkpoint interpretation are the main risk. Failure means recovered link count is outside the allowed range.
