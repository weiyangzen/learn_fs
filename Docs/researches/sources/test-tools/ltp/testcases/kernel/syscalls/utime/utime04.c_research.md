<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime04.c

Purpose: verifies privileged `utime(path, &times)` can set exact access and modification timestamps on a read-only file.

Important APIs/types/functions: global `times` contains `actime=20000` and `modtime=10000`. `setup()` creates `mntpoint/tmp_file` with mode `0444`; `run()` calls `utime()` and validates `st_mtime` and `st_atime` through `SAFE_STAT()` and `TST_EXP_EQ_LI`.

Control flow/state: single positive syscall path after setup. Persistent state is the timestamp pair on the temporary mounted file.

Dependencies/integration: requires root and LTP mounted filesystem coverage, with `vfat`/`exfat` skipped due to timestamp/permission differences.

Risks/test signals: failures are exact timestamp mismatches or permission/syscall errors. Because it checks second-resolution `st_atime/st_mtime`, filesystems with nonstandard rounding are the main portability risk.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/utime/utime04.c -->
