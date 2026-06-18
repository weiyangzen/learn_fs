<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime01.c

Purpose: verifies root-owned execution of `utime(path, NULL)` updates a file's access and modification times to the current filesystem timestamp window after first proving explicit `utimbuf` values are honored.

Important APIs/types/functions: `setup()` creates `mntpoint/tmp_file` with mode `0444`; `run()` uses `utime()`, `SAFE_STAT()`, `tst_fs_timestamp_start/end()`, `TST_EXP_PASS`, and `TST_EXP_EQ_LI`. The `tst_test` metadata requires root, a mounted test device, all filesystem coverage, and skips `vfat`/`exfat`.

Control flow/state: the test first sets deterministic old atime/mtime, validates them, then calls `utime(TEMP_FILE, NULL)` and compares both timestamps against the pre/post window. Persistent state is one mounted test file whose timestamps are mutated.

Dependencies/integration: uses LTP clock helpers to handle filesystem timestamp granularity and common mount orchestration for cross-filesystem testing.

Risks/test signals: failures are timestamp range mismatches or syscall errors. Filesystems with weak timestamp semantics are skipped; remaining flakes usually indicate granularity, clock, or permission behavior differences.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime01.c -->
