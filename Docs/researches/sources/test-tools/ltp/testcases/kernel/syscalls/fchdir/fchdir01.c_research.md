# sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir01.c

Purpose: positive `fchdir(2)` test that creates a directory, opens it, and verifies changing current working directory by file descriptor succeeds.

Important APIs/types/functions: `fchdir`, `SAFE_MKDIR`, `SAFE_OPEN`, `SAFE_CLOSE`, `TST_EXP_PASS`, and `struct tst_test`.

Control flow: `setup()` creates `alpha` in an LTP temp directory and opens it read-only. `verify_fchdir()` calls `fchdir(fd)` and records pass/fail through the LTP expectation macro. `cleanup()` closes the descriptor.

State/persistence behavior: creates one temporary directory and keeps an open directory fd across the test. The process cwd is changed during the test, but the LTP tempdir harness owns surrounding cleanup.

Dependencies/integration: uses the modern `tst_test.h` API with `.needs_tmpdir = 1`.

Risks/test signals: narrow success-path coverage. Failure indicates the directory fd was invalid, filesystem behavior is unexpected, or `fchdir` failed on a valid directory descriptor.
