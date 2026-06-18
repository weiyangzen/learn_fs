<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umount2.c -->
# sources/test-tools/strace/tests/umount2.c

## Purpose
Covers strace decoder coverage for `umount2`. Source read: 36 lines, 933 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <unistd.h>, <sys/stat.h>, <sys/mount.h>, "scno.h"; defines/undefs: TEST_SYSCALL_NR, TEST_SYSCALL_STR; C functions: main; syscall numbers/wrappers: umount2, umount, TEST_SYSCALL_NR.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: umount2, umount, TEST_SYSCALL_NR.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umount2.c -->
