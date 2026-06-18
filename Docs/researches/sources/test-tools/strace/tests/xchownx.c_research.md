<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xchownx.c -->
# sources/test-tools/strace/tests/xchownx.c

## Purpose
Covers strace decoder coverage for `xchownx`. Source comments/macros state: Check decoding of chown/chown32/lchown/lchown32/fchown/fchown32 syscalls. Source read: 139 lines, 2925 bytes.

## Important APIs, Types, And Functions
includes/imports: <fcntl.h>, <stdio.h>, <unistd.h>; defines/undefs: UGID_TYPE, GETEUID, GETEGID, CHECK_OVERFLOWUID, CHECK_OVERFLOWGID, UNLINK_SAMPLE, CLOSE_SAMPLE, SYSCALL_ARG1, FMT_ARG1, EOK_CMD, CLEANUP_CMD, PAIR; C functions: ugid2int, print_int, num_matches_id, main; syscall numbers/wrappers: geteuid, getegid, __NR_geteuid, __NR_getegid, SYSCALL_NR; harness commands: # define CHECK_OVERFLOWUID(arg) check_overflowuid(arg), # define CHECK_OVERFLOWGID(arg) check_overflowgid(arg).

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: geteuid, getegid, __NR_geteuid, __NR_getegid, SYSCALL_NR.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xchownx.c -->
