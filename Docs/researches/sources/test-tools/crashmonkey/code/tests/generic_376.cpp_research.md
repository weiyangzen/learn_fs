# sources/test-tools/crashmonkey/code/tests/generic_376.cpp

Purpose: btrfs generic/376 reproduction. It renames `test_dir/foo` to `bar`, creates a new `foo`, fsyncs `bar`, and expects both names to survive recovery.

Important APIs/types/functions: `Generic376`, `mkdir`, `open`, `fsync`, `rename`, `Checkpoint`, `opendir`/`readdir`, and `DataTestResult`.

Control flow: setup creates `test_dir/foo`, fsyncs the directory and file, then syncs. Run renames `foo` to `bar`, opens `bar`, creates a new `foo`, fsyncs only `bar`, checkpoints, and closes. Check enumerates `test_dir` for both `foo` and `bar`.

State/persistence behavior: the new file at the old name must not be lost just because only the renamed file was fsynced. The old and new inode names should coexist after checkpoint 1.

Dependencies/integration: direct POSIX operations and fixed `/mnt/snapshot`.

Risks/test signals: no content validation, only namespace presence. Failure reports missing `foo`, `bar`, or both.
