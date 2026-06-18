# sources/test-tools/crashmonkey/code/tests/sub_dir_mmap.cpp

Purpose: handwritten CrashMonkey workload that writes one 1 KiB random payload into a file under a synced subdirectory using `mmap`. It verifies, after crash/replay, that file metadata and byte contents match the generated random buffer.

Important APIs/types/functions: `BaseTestCase`, `DataTestResult`, `mkdir`, `open`, `fsync`, `/dev/urandom`, `ftruncate`, `mmap`, `memcpy`, `munmap`, `stat`, `read`, `memcmp`, and factory exports. Constants fix `/mnt/snapshot/test_dir`, one `test_file0`, 0777 permissions, and 1 KiB data size.

Control flow: `setup` creates and fsyncs the directory and fills `text` from `/dev/urandom`. `run` creates/truncates each test file, maps it shared writable, copies `text`, unmaps, closes, and returns `1` to signal a checkpoint boundary. `check_test` stats each file, validates type and permissions, reads exactly 1 KiB, and compares bytes to `text`.

State/persistence behavior: setup persists the directory before the test operation; the test write is through shared mmap without explicit msync. The oracle expects the file to exist with correct mode and full random contents after the tested crash state.

Dependencies/integration: assumes `/mnt/snapshot`, POSIX mmap, readable `/dev/urandom`, and CrashMonkey's BaseTestCase lifecycle preserving the in-memory `text` for checking. Risks/test signals: no `msync` means success can depend on implicit writeback timing; `if (file_data <= 0)` is a weak mmap failure check compared with `MAP_FAILED`.
