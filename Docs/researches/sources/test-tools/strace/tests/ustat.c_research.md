<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ustat.c -->
# sources/test-tools/strace/tests/ustat.c

## Purpose
Covers strace decoder coverage for `ustat`. Source comments/macros state: HAVE_USTAT_H Source read: 66 lines, 1505 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <sys/stat.h>, <sys/sysmacros.h>, <unistd.h>, <ustat.h>; defines/undefs: none; C functions: main; syscall numbers/wrappers: ustat, __NR_ustat; struct types: ustat, stat.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: ustat, __NR_ustat.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ustat.c -->
