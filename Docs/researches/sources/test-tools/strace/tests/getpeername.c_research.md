<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getpeername.c -->
# sources/test-tools/strace/tests/getpeername.c

## Purpose
Covers strace decoder coverage for `getpeername`. Source comments describe: Check decoding of getpeername syscall. Source read: 43 lines, 913 bytes.

## Important APIs, Types, And Functions
includes/imports: "sockname.c"; defines: TEST_SYSCALL_NAME; C functions: main; syscall names/numbers: cfd; struct types: sockaddr_un.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. primary syscall coverage is cfd.

## State And Persistence Behavior
creates local sockets and socket option state only for the duration of the process.

## Dependencies And Integration Points
Depends on shared implementation `sockname.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getpeername.c -->
