# sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvmsg/recvmsg01.c` is a 486-line LTP source file in the `recvmsg` syscall test area. recvmsg coverage for msghdr/iovec/control-message validation, stream/UNIX sockets, SCM_RIGHTS, and permission/error paths.

## Important APIs, Types, and Functions

called APIs/macros: `read`, `recvmsg`, `SAFE_ACCEPT`, `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_FORK`, `SAFE_GETSOCKNAME`, `SAFE_LISTEN`, `SAFE_OPEN`, `SAFE_SEND`, `SAFE_SENDMSG`, `SAFE_SIGNAL`, `SAFE_SOCKET`, `SAFE_UNLINK`, `TEST`; local functions: `setup_all`, `setup_invalid_sock`, `setup_valid_sock`, `setup_valid_msg_control`, `setup_large_msg_control`, `cleanup_all`, `cleanup_invalid_sock`, `cleanup_close_sock`, `cleanup_reset_all`, `do_child`, `start_server`, `run`, `sender`; struct/table types referenced: `struct sockaddr_in`, `struct sockaddr_un`, `struct msghdr`, `struct cmsghdr`, `struct iovec`, `struct tcase`, `struct sockaddr`, `struct timeval`, `struct tst_test`; important macros/constants: `MSG`, `BUF_SIZE`, `CONTROL_LEN`.

## Control Flow

Function-level flow is organized around `setup_all`, `setup_invalid_sock`, `setup_valid_sock`, `setup_valid_msg_control`, `setup_large_msg_control`, `cleanup_all`, `cleanup_invalid_sock`, `cleanup_close_sock`, `cleanup_reset_all`, `do_child`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is socket and child-server state: AF_INET and AF_UNIX listener sockets, connected clients, iovec buffers, control-message buffers, SCM_RIGHTS temporary files, and process lifetime controlled by the LTP fork harness.

## Dependencies and Integration Points

Direct includes: `<stdio.h>`, `<stdlib.h>`, `<sys/wait.h>`, `"tst_test.h"`. Uses the modern LTP `tst_test` harness for setup, cleanup, variants, filesystem requirements, and result reporting. Designated initializer fields seen include `.domain`, `.type`, `.iov`, `.iovcnt`, `.recv_buf`, `.buflen`, `.msg`, `.from`, `.fromlen`, `.exp_errno`, `.setup`, `.cleanup`, `.desc`, `.flags`, `.test`, `.tcnt`, `.forks_child`, `.needs_tmpdir`.

## Risks and Edge Cases

Socket tests are race-prone around child-server readiness, select timeouts, control-message sizing, and architecture-specific errno ordering. Cleanup must kill the child and unlink UNIX socket paths. Explicit errno expectations include `EBADF`, `ENOTSOCK`, `EINVAL`, `EFAULT`, `EMSGSIZE`, `EAGAIN`, `EINTR`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; TBROK for fixture/setup failures; notable reported messages include `invalid socket`; `invalid socket length`; `%s: expected %d, returned %ld`; `%s: expected %s`; `%s passed`.
