<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice02.c

Purpose: negative `vmsplice()` errno coverage for invalid fd, non-pipe fd, and too many iovec segments.

Important APIs/types/functions: `tcases[]` maps descriptor pointer, `iovec`, segment count, and expected errno: `EBADF` for `-1`, `EBADF` for a regular file, and `EINVAL` for `IOV_MAX + 1`. `setup()` opens a temp file, creates a pipe, and initializes the iovec.

Control flow/state: each test case calls `vmsplice()` once and checks return `-1` plus errno. State consists of one regular fd, one pipe, and a static buffer.

Dependencies/integration: uses LTP tmpdir and Linux `vmsplice` lapi wrapper; skips NFS for the regular file fixture.

Risks/test signals: errno expectations are the signal. If a kernel accepts a non-pipe fd or overlarge iov count, the test fails as a syscall contract regression.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/vmsplice/vmsplice02.c -->
