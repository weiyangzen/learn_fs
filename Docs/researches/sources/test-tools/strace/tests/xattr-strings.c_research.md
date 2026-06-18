<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/xattr-strings.c -->
# sources/test-tools/strace/tests/xattr-strings.c

## Purpose
Covers strace decoder coverage for `xattr-strings`. Source read: 37 lines, 721 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <stdio.h>, <sys/xattr.h>; defines/undefs: none; C functions: main.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
may create temporary extended attributes for successful xattr decoding.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`; unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/xattr-strings.c -->
