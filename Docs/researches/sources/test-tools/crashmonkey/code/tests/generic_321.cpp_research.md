# sources/test-tools/crashmonkey/code/tests/generic_321.cpp

Purpose: one copy of the xfstests generic/321 rename test. It creates `foo` at the mount root, creates directory `test_dir_a`, moves `foo` into that directory, fsyncs the directory/file, and expects the namespace to reflect the move after recovery.

Important APIs/types/functions: class name is `Generic321_2`; it uses `open`, `mkdir`, `fsync`, `rename`, `Checkpoint`, `opendir`/`readdir`, `stat`, and `DataTestResult`.

Control flow: setup creates the root file and target directory, fsyncs the file, and syncs. Run renames `foo` to `test_dir_a/foo`, fsyncs the destination directory and file, and checkpoints. Check enumerates root and `test_dir_a` to ensure the root only has the directory and the directory contains `foo`.

State/persistence behavior: old root name must disappear and new directory entry must be durable after checkpoint 1.

Dependencies/integration: direct POSIX namespace operations and CrashMonkey checkpointing.

Risks/test signals: this file duplicates much of `generic_321_2.cpp`. Signal is missing moved file, old file persistence, or unexpected directory contents.
