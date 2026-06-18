# sources/test-tools/crashmonkey/code/tests/checkpoint_example.cpp

Purpose: example CrashMonkey test showing how user checkpoints divide a workload and how `check_test()` interprets the last durable checkpoint. It creates a directory, writes a text file, checkpoints after directory/file persistence, then renames the file.

Important APIs/types/functions: `CheckpointExample`, `BaseTestCase`, `Checkpoint`, POSIX `mkdir`, `open`, `write`, `fsync`, `rename`, `stat`, `read`, and `memcmp`. It reports `kFileMissing`, `kOldFilePersisted`, metadata corruption, and data corruption through `DataTestResult`.

Control flow: `run()` fsyncs the new directory and root, takes checkpoint 1, writes the War and Peace text into `old_file`, fsyncs the file and root, takes checkpoint 2, then renames `old_file` to `new_file`. `check_test()` decides whether to inspect the old or new pathname based on checkpoint reachability.

State/persistence behavior: checkpoint 1 requires the directory to exist; checkpoint 2 requires the file contents, type, and permissions to be durable. The rename is intentionally after checkpoint 2, so recovery may validly show either name unless the checkpoint implies otherwise.

Dependencies/integration: exercises checkpoint accounting, file data validation, directory fsync ordering, and CrashMonkey's replay/oracle split.

Risks/test signals: the test has static `/mnt/snapshot` paths and uses a large UTF-8 string literal. Its strongest signal is detecting missing files, stale old name persistence after rename is expected to have landed, or byte mismatches in recovered content.
