<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/tcp_ao.c -->
# sources/test-tools/strace/tests/tcp_ao.c

## Purpose
Covers strace decoder coverage for `tcp_ao`. Source comments/macros state: Check decoding of TCP_AO_ADD_KEY socket option. Source read: 116 lines, 3409 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <linux/tcp.h>, <netinet/in.h>, <stddef.h>, <stdio.h>, <string.h>, <sys/socket.h>, <unistd.h>; defines/undefs: KEY1, KEY2; C functions: add_key, main; struct types: tcp_ao_add, sockaddr_in6, sockaddr_in.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. temporary kernel objects are created to exercise descriptor, timer, or socket decoding.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries; creates transient socket state for local decoding.

## Dependencies And Integration Points
Depends on `tests.h`, Linux UAPI headers. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/tcp_ao.c -->
