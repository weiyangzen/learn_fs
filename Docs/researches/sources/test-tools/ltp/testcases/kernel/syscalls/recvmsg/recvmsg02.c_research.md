# sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg02.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg02.c` is a 103-line LTP source file in the `recvmsg` syscall test area. recvmsg coverage for msghdr/iovec/control-message validation, stream/UNIX sockets, SCM_RIGHTS, and permission/error paths.

## Important APIs, Types, and Functions

called APIs/macros: `recvmsg`, `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_GETSOCKNAME`, `SAFE_SOCKET`; local functions: `verify_recvmsg`, `cleanup`; struct/table types referenced: `struct sockaddr_in6`, `struct iovec`, `struct msghdr`, `struct sockaddr`, `struct tst_test`, `struct tst_tag`.

## Control Flow

Function-level flow is organized around `verify_recvmsg`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state.

## State and Persistence Behavior

State is socket and child-server state: AF_INET and AF_UNIX listener sockets, connected clients, iovec buffers, control-message buffers, SCM_RIGHTS temporary files, and process lifetime controlled by the LTP fork harness.

## Dependencies and Integration Points

Direct includes: `<string.h>`, `<stdio.h>`, `<stdlib.h>`, `<unistd.h>`, `<sys/types.h>`, `<sys/socket.h>`, `<netinet/in.h>`, `"tst_test.h"`, `"lapi/socket.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.sin6_family`, `.sin6_port`, `.sin6_addr`, `.iov_base`, `.iov_len`, `.msg_name`, `.msg_namelen`, `.msg_iov`, `.msg_iovlen`, `.msg_control`, `.msg_controllen`, `.msg_flags`, `.test_all`, `.cleanup`, `.tags`. Depends on LTP `lapi` wrappers for direct syscall numbers, compatibility structures, or missing libc declarations.

## Risks and Edge Cases

Socket tests are race-prone around child-server readiness, select timeouts, control-message sizing, and architecture-specific errno ordering. Cleanup must kill the child and unlink UNIX socket paths.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `lapi/socket.h`; `recvmsg(..., MSG_PEEK) failed`.
