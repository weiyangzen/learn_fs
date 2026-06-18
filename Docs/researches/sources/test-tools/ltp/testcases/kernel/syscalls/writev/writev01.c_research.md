<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev01.c

Purpose: basic and negative `writev()` coverage for invalid iovec length, invalid fd, invalid iovcnt, zero iovcnt, NULL zero-length iovecs, and closed-pipe `EPIPE`.

Important APIs/types/functions: `iovec_badlen`, `iovec_simple`, and `iovec_zero_null` define vector shapes. `testcases[]` encodes expected return and errno. `setup()` blocks `SIGPIPE`, opens a regular file, creates a pipe, and closes the read end.

Control flow/state: each row calls `writev()` once and compares return/errno against the table. File and pipe descriptors are shared fixtures.

Dependencies/integration: uses modern LTP harness and tmpdir. Blocking SIGPIPE keeps the closed-pipe case observable as `EPIPE` without terminating the test.

Risks/test signals: architecture/libc handling of negative `iov_len` represented in `size_t` is the main portability edge. Expected successes are exact byte counts; expected failures require exact errno.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/writev01.c -->
