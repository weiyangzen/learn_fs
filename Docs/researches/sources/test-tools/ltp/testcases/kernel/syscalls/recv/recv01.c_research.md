# sources/test-tools/ltp/testcases/kernel/syscalls/recv/recv01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recv/recv01.c` is a 281-line LTP source file in the `recv` syscall test area. recv socket syscall coverage across stream/datagram descriptors, invalid arguments, and expected network errno paths.

## Important APIs, Types, and Functions

called APIs/macros: `read`, `recv`, `socket`, `connect`, `bind`, `listen`, `accept`, `SAFE_GETSOCKNAME`, `SAFE_SOCKET`, `TEST`; local functions: `do_child`, `start_server`, `main`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`; struct/table types referenced: `struct sockaddr_in`, `struct test_case_t`, `struct timeval`, `struct sockaddr`.

## Control Flow

Function-level flow is organized around `do_child`, `start_server`, `main`, `setup`, `cleanup`, `setup0`, `cleanup0`, `setup1`, `cleanup1`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. This file uses the older `test.h` harness: `main` parses options, loops over configured cases or signals, calls direct syscall wrappers, reports through `tst_resm`/`tst_brkm`, and exits through `tst_exit`. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is socket state: file descriptors, sockaddr structures, send/receive buffers, optional child servers, and errno values returned by the network stack.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<unistd.h>`, `<errno.h>`, `<fcntl.h>`, `<sys/types.h>`, `<sys/socket.h>`, `<sys/signal.h>`, `<sys/un.h>`, `<netinet/in.h>`, `"test.h"`, `"tso_safe_macros.h"`. Uses the older LTP `test.h` harness and legacy result macros.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; signal or child-process synchronization must avoid races Explicit errno expectations include `EBADF`, `ENOTSOCK`, `EFAULT`, `EINVAL`, `EAGAIN`, `EINTR`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `invalid socket`; ` %ld (expected %d), errno %d (expected`; `connect failed`; `client setup1 failed - no message ready in 2 sec`; `server socket failed`.
