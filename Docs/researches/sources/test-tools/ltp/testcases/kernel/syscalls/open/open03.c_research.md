# sources/test-tools/ltp/testcases/kernel/syscalls/open/open03.c

Purpose: minimal positive `open(2)` test for `O_RDWR|O_CREAT`. Important APIs/types/functions: `TST_EXP_FD(open(...))`, `SAFE_CLOSE`, and `SAFE_UNLINK`. Control flow: create/open `testfile` with mode `0700`, close the returned fd, and unlink it. State/persistence: transient file in LTP tempdir. Dependencies/integration: modern `tst_test` `.needs_tmpdir`. Risks: narrow smoke test only checks that the open returns a valid fd. Test signals: pass means basic create/open/close/unlink workflow succeeds.
