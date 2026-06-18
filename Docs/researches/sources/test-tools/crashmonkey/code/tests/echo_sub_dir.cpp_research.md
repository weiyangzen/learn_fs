# sources/test-tools/crashmonkey/code/tests/echo_sub_dir.cpp

Purpose: simple file-in-subdirectory persistence test. It creates `test_dir`, writes a small constant text string to `test_dir/foo`, fsyncs the file, and expects the file and data to survive recovery.

Important APIs/types/functions: `echo_sub_dir`, `BaseTestCase`, POSIX `mkdir`, `open`, `write`, `fsync`, `stat`, `read`, and `DataTestResult`.

Control flow: `setup()` creates and fsyncs the directory. `run()` opens the file with `O_RDWR | O_CREAT`, writes the complete `TEXT` string in a loop, calls `fsync(fd)`, then returns success. `check_test()` stats and reads the file.

State/persistence behavior: after the file fsync, the file should be regular, have the expected mode/size, and contain the exact text bytes. The directory is persisted before the workload, so the check is focused on file data and inode metadata.

Dependencies/integration: uses fixed `/mnt/snapshot/test_dir/foo` paths and direct syscalls rather than `cm_` wrappers.

Risks/test signals: because there is no explicit CrashMonkey `Checkpoint()`, the harness records no intermediate user checkpoint; the workload is best as a basic fully-run crash image. Errors are file missing, metadata mismatch, read failure, or byte corruption.
