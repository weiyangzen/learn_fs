<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit.c -->
# sources/test-tools/strace/tests/strace--syscall-limit.c

## Purpose
Covers the `--syscall-limit` option and related summary/status interactions. Source comments/macros state: Test --syscall-limit option. !PRINT_VALID PRINT_VALID print print print the tracer is expected to detach at this point if TOTAL_CNT < 4. print the tracer is expected to detach at this point print PRINT_STATS Source read: 151 lines, 3181 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <errno.h>, <fcntl.h>, <stdio.h>, <stdlib.h>, <unistd.h>, <sys/types.h>, <sys/wait.h>; defines/undefs: PRINT_VALID, PRINT_INVALID, PRINT_STATS, UNLINKAT_CNT, TOTAL_CNT, AT_FDCWD, AT_REMOVEDIR; C functions: write_status, test_chdir, test_rmdir, main; syscall numbers/wrappers: unlinkat, __NR_unlinkat.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. process/thread branches synchronize children or threads before final trace comparison. primary syscall coverage: unlinkat, __NR_unlinkat.

## State And Persistence Behavior
owns transient child/thread lifecycle state that must be synchronized before exit.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; process/thread ordering can make trace matching fragile. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace--syscall-limit.c -->
