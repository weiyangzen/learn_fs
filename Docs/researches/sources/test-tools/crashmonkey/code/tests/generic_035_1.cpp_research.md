# sources/test-tools/crashmonkey/code/tests/generic_035_1.cpp

Purpose: file rename variant of xfstests generic/035. It renames one file over another in the same directory and fsyncs the destination name, then checks that directory metadata is clean after removing the surviving file.

Important APIs/types/functions: source class is named `Generic321_1`; it uses `mkdir`, `open`, `rename`, `fstat`, `fsync`, `Checkpoint`, `remove`, `rmdir`, and `DataTestResult`.

Control flow: `setup()` creates a directory and two files, then syncs. `run()` opens the original destination, renames `file1` over `file2`, uses `fstat` for sanity, reopens/fsyncs `file2`, and checkpoints. `check_test()` removes `file2` and expects `rmdir` of the parent to succeed.

State/persistence behavior: the renamed-over entry should not leave stale directory state or hidden references after recovery. Persistence focus is namespace replacement and destination inode logging.

Dependencies/integration: direct POSIX rename/fsync workload with `/mnt/snapshot`-derived paths.

Risks/test signals: class naming is misleading because it says `Generic321_1`. The primary signal is inability to remove an apparently empty directory, reported as metadata corruption.
