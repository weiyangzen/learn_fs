# sources/test-tools/ltp/testcases/kernel/syscalls/fchownat/fchownat01.c

Purpose: positive `fchownat(2)` functionality test for `AT_FDCWD` and directory-fd relative path resolution.

Important APIs/types/functions: `fchownat`, `SAFE_OPEN` with `O_DIRECTORY`, `SAFE_TOUCH`, `SAFE_STAT`, `TST_EXP_PASS`, and `TST_EXP_EQ_LI`.

Control flow: setup opens the current temp directory and creates two files. The test first calls `fchownat(AT_FDCWD, TESTFILE1, 1000, 1000, 0)` and verifies ownership, then calls `fchownat(dir_fd, TESTFILE2, 1000, 1000, 0)` and verifies ownership.

State/persistence behavior: mutates ownership of two temp files to numeric uid/gid 1000.

Dependencies/integration: requires root and tempdir. It assumes numeric uid/gid values are accepted even if no matching accounts exist.

Risks/test signals: failures isolate either `AT_FDCWD` or directory-fd path resolution. Wrong uid/gid after stat fails.
