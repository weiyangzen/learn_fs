# sources/test-tools/ltp/testcases/kernel/syscalls/eventfd2/eventfd2_01.c

Purpose: Verifies that `eventfd2()` honors `EFD_CLOEXEC` by setting `FD_CLOEXEC` on the returned descriptor.

Important APIs/types/functions: `eventfd2()` from the local header, `SAFE_FCNTL(fd, F_GETFD)`, `FD_CLOEXEC`, `TST_EXP_EXPR`, and `SAFE_CLOSE`.

Control flow: The test creates one descriptor without flags and expects no close-on-exec bit, closes it, then creates another descriptor with `EFD_CLOEXEC` and expects the bit to be present.

State and persistence behavior: State is descriptor metadata in the per-process file descriptor table; no filesystem or counter persistence matters.

Dependencies and integration points: Integrates the raw syscall wrapper with POSIX `fcntl` flag inspection.

Risks and test signals: A regression in flag propagation or wrapper argument order is detected as a mismatched `FD_CLOEXEC` bit.
