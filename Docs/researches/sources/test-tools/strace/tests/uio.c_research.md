<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/uio.c -->
# sources/test-tools/strace/tests/uio.c

## Purpose
Covers strace decoder coverage for `uio`. Source read: 43 lines, 874 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <fcntl.h>, <unistd.h>, <sys/uio.h>, <assert.h>; defines/undefs: none; C functions: main; struct types: iovec.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations.

## State And Persistence Behavior
touches temporary filesystem names or descriptors and cleans them through harness/process lifetime.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/uio.c -->
