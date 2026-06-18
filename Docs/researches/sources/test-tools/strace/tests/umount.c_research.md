<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/umount.c -->
# sources/test-tools/strace/tests/umount.c

## Purpose
Covers strace decoder coverage for `umount`. Source read: 47 lines, 933 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <sys/stat.h>, <sys/mount.h>, "scno.h", <unistd.h>; defines/undefs: TEST_SYSCALL_STR, __NR_oldumount; C functions: main; syscall numbers/wrappers: oldumount, umount, umount2, __NR_oldumount.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: oldumount, umount, umount2, __NR_oldumount.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/umount.c -->
