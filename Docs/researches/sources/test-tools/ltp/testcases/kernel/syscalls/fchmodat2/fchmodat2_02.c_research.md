# sources/test-tools/ltp/testcases/kernel/syscalls/fchmodat2/fchmodat2_02.c

Purpose: negative `fchmodat2(2)` argument validation for bad fd, missing file, and invalid flags.

Important APIs/types/functions: `tst_syscall(__NR_fchmodat2)`, `SAFE_TOUCH`, `SAFE_OPEN`, `tst_tmpdir_path`, `O_PATH | O_DIRECTORY`, `TST_EXP_FAIL`, and errno constants `EBADF`, `ENOENT`, `EINVAL`.

Control flow: setup records the tempdir path, creates `file.bin`, and opens the temp directory as an `O_PATH` directory fd. Each table case invokes raw `fchmodat2` and checks the expected errno.

State/persistence behavior: creates one file and one directory fd; no successful chmod should occur.

Dependencies/integration: uses LTP syscall-number wrappers and tempdir helpers.

Risks/test signals: narrow errno test. If a libc wrapper or kernel changes validation order, expected errno may need review.
