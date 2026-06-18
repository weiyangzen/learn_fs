# sources/test-tools/crashmonkey/code/tests/echo_sub_dir_no_sync.cpp

Purpose: contrast workload for the synced echo test. It writes the same small file in a synced directory but intentionally omits the file `fsync`, probing what the checker currently assumes for unflushed data.

Important APIs/types/functions: `echo_sub_dir_no_sync`, `mkdir`, directory `fsync`, `open`, `write`, `stat`, `read`, and `DataTestResult`.

Control flow: `setup()` creates and fsyncs `test_dir`. `run()` opens `test_dir/foo`, writes the constant text in a loop, and closes/returns without forcing file data to stable storage. `check_test()` still expects the file to exist with the full size and contents.

State/persistence behavior: only the parent directory is durably established before the file write. The file contents are deliberately not synchronized, so this test is useful for observing filesystem behavior but has a stricter oracle than POSIX crash semantics would normally guarantee.

Dependencies/integration: direct POSIX syscalls and fixed `/mnt/snapshot` paths; no CrashMonkey checkpoint calls.

Risks/test signals: because the file data is not fsynced, failures may be expected on conservative filesystems. Signals remain missing file, metadata mismatch, read failure, or text mismatch.
