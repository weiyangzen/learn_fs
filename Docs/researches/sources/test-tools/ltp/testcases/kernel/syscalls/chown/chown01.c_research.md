# sources/test-tools/ltp/testcases/kernel/syscalls/chown/chown01.c

Purpose: basic positive `chown()` test on a tmp file. Setup validates current euid/egid with 16-bit compatibility checks and creates `chown01_testfile`; run calls `CHOWN` to set the file to the same uid/gid and expects success. Important APIs are `CHOWN` from `compat_tst_16.h`, `UID16_CHECK`, `GID16_CHECK`, and `SAFE_FILE_PRINTF`. State is one temporary file. Dependencies are tmpdir and chown syscall support. Risks are uid/gid compatibility on old ABI variants. Test signal is `chown` success.
