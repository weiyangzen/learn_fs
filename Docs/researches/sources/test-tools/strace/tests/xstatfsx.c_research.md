<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xstatfsx.c -->
# sources/test-tools/strace/tests/xstatfsx.c

## Purpose
Covers strace decoder coverage for `xstatfsx`. Source read: 108 lines, 2647 bytes.

## Important APIs, Types, And Functions
includes/imports: <stdio.h>, <fcntl.h>, <unistd.h>, <linux/types.h>, <asm/statfs.h>, "xlat.h", "xlat/fsmagic.h", "xlat/statfs_flags.h"; defines/undefs: PRINT_NUM; C functions: print_statfs_type, print_statfs, main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `xlat.h`, Linux UAPI headers, procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xstatfsx.c -->
