<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex.c -->
# sources/test-tools/strace/tests/futex.c

## Purpose
Covers strace self-test coverage for `futex`. Source comments describe: It is here due to EPERM on WAKE_OP on AArch64 Since timeout value is copied before full op check, we should provide some valid timeout address or NULL FUTEX_??? Value which differs from one stored in int *val FUTEX_WAIT - check whether uaddr == val and sleep Possible flags: PRIVATE, CLOCK_RT (since 4.5) 1. uaddr - futex address 2. op - FUTEX_WAIT 3. val -. Source read: 820 lines, 31098 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <stdarg.h>, <stdio.h>, <stdint.h>, <unistd.h>, <sys/time.h>, "xlat.h", "xlat/futexops.h", "xlat/futexwakeops.h", "xlat/futexwakecmps.h"; defines: FUTEX_PRIVATE_FLAG, FUTEX_CLOCK_REALTIME, FUTEX_CMD_MASK, CHECK_FUTEX_GENERIC, CHECK_FUTEX_ENOSYS, CHECK_FUTEX, CHECK_INVALID_CLOCKRT, VAL, VAL_PR, VALP, VALP_PR, VAL2, VAL2_PR, VAL2P, VAL2P_PR, VAL3, VAL3_PR, VAL3A; C functions: futex_error, invalid_op, main; syscall names/numbers: futex, __NR_futex.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations. primary syscall coverage is futex, __NR_futex.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `xlat.h`, configured syscall-number availability. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall, requiring ENOSYS/skip handling. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex.c -->
