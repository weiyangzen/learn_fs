<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sysctl.c -->
# sources/test-tools/strace/tests/sysctl.c

## Purpose
Covers strace decoder coverage for `sysctl`. Source comments/macros state: Check decoding of sysctl syscall. Source read: 63 lines, 1362 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <string.h>, <unistd.h>, <linux/sysctl.h>; defines/undefs: none; C functions: k_sysctl, main; syscall numbers/wrappers: _sysctl, __NR__sysctl; struct types: __sysctl_args.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. primary syscall coverage: _sysctl, __NR__sysctl.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, Linux UAPI headers, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sysctl.c -->
