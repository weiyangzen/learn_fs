<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/inet-cmsg.c -->
# sources/test-tools/strace/tests/inet-cmsg.c

## Purpose
Covers strace self-test coverage for `inet-cmsg`. Source read: 176 lines, 4238 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <fcntl.h>, <stdio.h>, <stdint.h>, <unistd.h>, <sys/socket.h>, <netinet/in.h>, <arpa/inet.h>; defines: SETSOCKOPT; C functions: print_pktinfo, print_ttl, print_tos, print_opts, print_origdstaddr, main; struct types: cmsghdr, sockaddr_in, sockaddr, iovec, msghdr.

## Control Flow
`main` prepares synthetic arguments, invokes the target syscall or libc wrapper, prints the expected strace line format, and ends with `+++ exited with 0 +++` where applicable. nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
opens descriptors, commonly `/dev/null`, `/dev/full`, or the current directory, for fd/path decoding; creates local sockets and socket option state only for the duration of the process.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: program stdout contains the canonical expected strace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/inet-cmsg.c -->
