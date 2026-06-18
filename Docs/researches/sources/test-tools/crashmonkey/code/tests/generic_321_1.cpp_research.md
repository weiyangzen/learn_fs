# sources/test-tools/crashmonkey/code/tests/generic_321_1.cpp

Purpose: directory creation subtest from xfstests generic/321. It verifies that a newly created directory survives recovery after the directory itself is fsynced.

Important APIs/types/functions: `Generic321_1`, `mkdir`, `open(..., O_DIRECTORY)`, `fsync`, `Checkpoint`, `stat`, and `DataTestResult`.

Control flow: `setup()` does nothing. `run()` creates `test_dir_a`, opens it as a directory, fsyncs it, checkpoints, and returns at checkpoint 1. `check_test()` validates the directory exists.

State/persistence behavior: the durable state is the presence of the newly created directory entry and directory inode after fsync/checkpoint.

Dependencies/integration: `mnt_dir_` path initialization and raw POSIX directory fsync support.

Risks/test signals: some filesystems have nuanced semantics for fsyncing a newly created directory without fsyncing its parent; the test expects persistence. Missing directory is the main failure.
