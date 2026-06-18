<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/strace-p1-Y-p.c -->
# sources/test-tools/strace/tests/strace-p1-Y-p.c

## Purpose
Covers strace command-line option behavior. Source comments/macros state: This file is part of strace-p-Y-p strace test. Source read: 43 lines, 827 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <stdlib.h>, <unistd.h>; defines/undefs: MY_COMM; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
no persistent repository or kernel state is intended; runtime state is local variables plus syscall return values.

## Dependencies And Integration Points
Depends on `tests.h`, procfs. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel configuration, procfs visibility, or privileges can change availability. Test signals: unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/strace-p1-Y-p.c -->
