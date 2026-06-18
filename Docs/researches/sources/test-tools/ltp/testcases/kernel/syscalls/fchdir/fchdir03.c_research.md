# sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/fchdir03.c

Purpose: verifies `fchdir(2)` fails with `EACCES` when an unprivileged effective user lacks execute/search permission on the target directory.

Important APIs/types/functions: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SAFE_MKDIR`, `SAFE_OPEN`, `fchdir`, `TEST`, `TST_RET`, `TST_ERR`, and `tst_res`.

Control flow: setup looks up `nobody`, switches effective uid to that user, creates `fchdir03_dir` with mode `0400`, and opens it. The test calls `fchdir(fd)`, expects `-1`, then specifically requires `TST_ERR == EACCES`.

State/persistence behavior: creates a temporary directory with no execute permission and permanently changes effective uid within the test process. The open fd remains global.

Dependencies/integration: requires root for `seteuid` and an LTP temp directory. It depends on the presence of the `nobody` account.

Risks/test signals: filesystem permission semantics are central. Incorrect privilege setup could turn this into a false pass/fail; success of `fchdir` or errno mismatch fails.
