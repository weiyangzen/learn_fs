<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/group_req.c -->
# sources/test-tools/strace/tests/group_req.c

## Purpose
Covers strace decoder coverage for `MCAST_JOIN_GROUP`. Source comments describe: Check decoding of MCAST_JOIN_GROUP/MCAST_LEAVE_GROUP. optlen < 0, EINVAL optlen < sizeof(struct group_req), EINVAL optval EFAULT classic optlen > sizeof(struct group_req), shortened Source read: 148 lines, 4172 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <net/if.h>, <netinet/in.h>, <limits.h>, <stdio.h>, <unistd.h>, <sys/socket.h>, <arpa/inet.h>; defines: multi4addr, multi6addr; C functions: set_opt, main; struct types: group_req, sockaddr_in, sockaddr_in6.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
uses tail-allocated buffers to create valid, short-read, and EFAULT-adjacent pointer cases; creates local sockets and socket option state only for the duration of the process.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines; return-code text from `sprintrc` is compared; skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/group_req.c -->
