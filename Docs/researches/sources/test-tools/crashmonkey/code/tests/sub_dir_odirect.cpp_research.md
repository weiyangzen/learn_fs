# sources/test-tools/crashmonkey/code/tests/sub_dir_odirect.cpp

Purpose: handwritten workload that writes one 1 KiB random payload into a file under a synced subdirectory using `O_DIRECT`. It tests direct-IO persistence and later validates file mode and data.

Important APIs/types/functions: `BaseTestCase`, `DataTestResult`, `mkdir`, directory `fsync`, `/dev/urandom`, `posix_memalign`, `open(...|O_DIRECT)`, 512-byte aligned `write`, `stat`, `read`, `memcmp`, and plugin exports. Constants use 1 KiB test data and 512-byte alignment.

Control flow: `setup` creates/fsyncs `test_dir` and fills `text`. `run` allocates aligned memory, copies `text`, creates `test_file0` with `O_DIRECT`, writes two 512-byte chunks until 1 KiB is written, closes, frees, and returns `1`. `check_test` stats the file, validates regular-file permissions, reads the full file, and compares data.

State/persistence behavior: direct writes bypass page cache, so the operation probes block-device and filesystem direct-IO ordering. Directory creation is synced separately; the file's data write has no explicit fsync after close.

Dependencies/integration: requires a filesystem/device accepting 512-byte aligned direct writes of 1 KiB. Risks/test signals: partial writes are handled, but allocation failure check uses `< 0` even though `posix_memalign` returns positive errno values on failure; failure modes are reported through `DataTestResult`.
