# sources/test-tools/crashmonkey/code/tests/generic_034.cpp

Purpose: reproduction of xfstests generic/034 for a btrfs directory-log replay bug. After creating `foo`, creating and fsyncing `bar`, and fsyncing the parent directory, recovered directory state should be removable after deleting entries.

Important APIs/types/functions: `Generic034`, `mkdir`, `open`, `fsync` on directory and file descriptors, `Checkpoint`, `remove`, `rmdir`, `errno == ENOTEMPTY`, and `DataTestResult::kFileMetadataCorrupted`.

Control flow: `setup()` creates `test_dir_a/foo` and syncs. `run()` creates `bar`, opens `test_dir_a`, fsyncs the directory, fsyncs `bar`, then checkpoints. `check_test()` removes `foo` and `bar` if present, then attempts to remove the directory.

State/persistence behavior: the expected durable state must not leave stale directory index/i_size information. Even if files are present and removable, `rmdir(test_dir_a)` must succeed once entries are deleted.

Dependencies/integration: fixed `/mnt/snapshot` paths, raw syscalls, and btrfs-inspired log replay semantics.

Risks/test signals: the check mutates recovered state while validating it. Failure signal is `rmdir` returning `ENOTEMPTY` after cleanup, meaning directory metadata is inconsistent.
