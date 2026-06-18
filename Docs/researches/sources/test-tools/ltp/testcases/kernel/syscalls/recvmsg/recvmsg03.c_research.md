# sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg03.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg03.c` is a 156-line LTP source file in the `recvmsg` syscall test area. recvmsg coverage for msghdr/iovec/control-message validation, stream/UNIX sockets, SCM_RIGHTS, and permission/error paths. Source description: Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions

called APIs/macros: `recvmsg`, `socket`, `sendmsg`, `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_FORK`, `SAFE_RECVMSG`, `SAFE_SOCKET`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`; local functions: `setup`, `client`, `server`, `verify_recvmsg`; struct/table types referenced: `struct sockaddr_in`, `struct msghdr`, `struct iovec`, `struct sockaddr`, `struct tst_test`, `struct tst_tag`; important macros/constants: `AF_RDS`.

## Control Flow

Function-level flow is organized around `setup`, `client`, `server`, `verify_recvmsg`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result.

## State and Persistence Behavior

State is socket and child-server state: AF_INET and AF_UNIX listener sockets, connected clients, iovec buffers, control-message buffers, SCM_RIGHTS temporary files, and process lifetime controlled by the LTP fork harness.

## Dependencies and Integration Points

Direct includes: `<errno.h>`, `<string.h>`, `<sys/types.h>`, `<sys/socket.h>`, `"tst_safe_net.h"`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.forks_child`, `.needs_checkpoints`, `.setup`, `.test_all`, `.tags`.

## Risks and Edge Cases

Socket tests are race-prone around child-server readiness, select timeouts, control-message sizing, and architecture-specific errno ordering. Cleanup must kill the child and unlink UNIX socket paths. Explicit errno expectations include `EAFNOSUPPORT`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TCONF for unsupported kernel, filesystem, or feature combinations; TBROK for fixture/setup failures; notable reported messages include `rds was not supported`; `socket() failed with rds`; `sendmsg() failed to send data to server`; `expected %lu`.
