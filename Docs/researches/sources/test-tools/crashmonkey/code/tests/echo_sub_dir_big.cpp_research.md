# sources/test-tools/crashmonkey/code/tests/echo_sub_dir_big.cpp

Purpose: larger variant of the echo-in-subdirectory test. It writes a sizeable random buffer to one or more files under a pre-synced directory and validates full content persistence after recovery.

Important APIs/types/functions: `echo_sub_dir_big`, `/dev/urandom`, `mkdir`, `open`, `write`, `fsync`, `stat`, `read`, and `DataTestResult`.

Control flow: `setup()` creates and fsyncs `test_dir`, then fills the test buffer from `/dev/urandom`. `run()` creates each target file under the directory, writes the whole buffer, fsyncs the file, and closes it. `check_test()` walks the expected file names and compares recovered contents against the saved random buffer.

State/persistence behavior: the test validates that file size, mode/type, and every byte of a larger buffered write reach durable state after `fsync`. It also covers parent-directory persistence because the directory is fsynced before file creation.

Dependencies/integration: direct POSIX workload with fixed `/mnt/snapshot` paths; uses process memory as the expected-content oracle.

Risks/test signals: random oracle state means the same object instance must perform run and check. The main signals are missing files, wrong size/mode, short reads, and byte mismatch.
