<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tkill.c -->
# sources/test-tools/strace/tests/tkill.c

## Purpose
Covers strace decoder coverage for `tkill`. Source comments/macros state: Check decoding of tkill syscall. Source read: 69 lines, 1512 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", "pidns.h", <signal.h>, <stdio.h>, <unistd.h>; defines/undefs: none; C functions: k_tkill, main; syscall numbers/wrappers: tkill, gettid, __NR_tkill, __NR_gettid.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: tkill, gettid, __NR_tkill, __NR_gettid.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, `pidns.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; pid namespace translation depends on namespace support and synchronization. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tkill.c -->
