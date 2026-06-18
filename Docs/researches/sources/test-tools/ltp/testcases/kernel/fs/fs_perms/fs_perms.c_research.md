# sources/test-tools/ltp/testcases/kernel/fs/fs_perms/fs_perms.c

Purpose: regression test for filesystem permission enforcement across read, write, and execute bits for a file with specified owner/group/mode and a tester uid/gid.

Important APIs/types/functions: `testsetup`, `testfperm`, `str_to_l`, `cleanup`, `tst_require_root`, `tst_tmpdir`, `tst_get_path`, `chmod`, `chown`, `fork`, `setgid`, `setuid`, `fopen`, `execl`, `execlp`, `wait`, and LTP `tst_resm`.

Control flow: validates seven arguments, parses file mode/owner/group/tester credentials/permission/expected result, creates an empty test file, and for execute tests also creates a shebang file. A child drops to the tester credentials and attempts either open mode `r`/`w` or execution. Parent compares child exit status with the expected result and reports one LTP pass/fail line.

State/persistence behavior: creates temporary files `test.file1` and optionally `test.file2` in an LTP temp directory, changes their ownership and modes, and removes the temp directory at completion.

Dependencies/integration: requires root to chown and switch credentials. Integrated with legacy LTP `test.h` rather than modern `tst_test.h`.

Risks/test signals: `wait(&status)` assumes normal child exit before `WEXITSTATUS`. Execute behavior differs for kernel shebang handling versus libc fallback, which is why two files are tested. Success is exact match between observed child result and expected result.
