# sources/test-tools/ltp/testcases/kernel/syscalls/recvmmsg/recvmmsg01.c

## Purpose

`sources/test-tools/ltp/testcases/kernel/syscalls/recvmmsg/recvmmsg01.c` is a 179-line LTP source file in the `recvmmsg` syscall test area. recvmmsg multi-message receive coverage for datagram sockets, timeout handling, and kernel feature availability. Source description: \ Test recvmmsg() errors: - EBADF  Bad socket file descriptor - EFAULT Bad message vector address - EINVAL Bad seconds value for the timeout argument - EINVAL Bad nanoseconds value for the timeout argument - EFAULT Bad timeout address

## Important APIs, Types, and Functions

called APIs/macros: `recvmmsg`, `SAFE_BIND`, `SAFE_CLOSE`, `SAFE_CONNECT`, `SAFE_FORK`, `SAFE_SOCKET`, `SAFE_WAITPID`, `TEST`, `TST_EXP_FAIL2`, `TST_GET_UNUSED_PORT`; local functions: `verify_recvmmsg`, `test_bad_addr`, `do_test`, `setup`, `cleanup`; struct/table types referenced: `struct mmsghdr`, `struct iovec`, `struct tst_ts`, `struct test_case`, `struct time64_variants`, `struct sockaddr_in`, `struct sockaddr`, `struct tst_test`, `struct tst_buffers`; important macros/constants: `_GNU_SOURCE`, `VLEN`.

## Control Flow

Function-level flow is organized around `verify_recvmmsg`, `test_bad_addr`, `do_test`, `setup`, `cleanup`. The LTP harness calls setup hooks to create files, mounts, sockets, keys, signal handlers, or descriptors, then dispatches either a per-case `.test` callback or a `.test_all` callback, and finally runs cleanup hooks to close descriptors and remove temporary state. Some flow is concurrent: child processes or pthreads are used to exercise server, signal-delivery, or permission behavior, with waits/checkpoints joining the result. Case tables drive repeated checks over expected success/error outcomes, descriptors, flags, quotas, signals, or policies.

## State and Persistence Behavior

State is socket state: file descriptors, sockaddr structures, send/receive buffers, optional child servers, and errno values returned by the network stack.

## Dependencies and Integration Points

Direct includes: `"../sendmmsg/sendmmsg.h"`. Designated initializer fields seen include `.desc`, `.fd`, `.exp_errno`, `.msg_vec`, `.tv_sec`, `.tv_nsec`, `.bad_ts_addr`, `.test`, `.tcnt`, `.setup`, `.cleanup`, `.test_variants`, `.forks_child`, `.bufs`.

## Risks and Edge Cases

bad-address cases are architecture and fault-path sensitive; signal or child-process synchronization must avoid races Explicit errno expectations include `EBADF`, `EFAULT`, `EINVAL`.

## Test Signals

TPASS/TST_EXP_PASS success reports; TFAIL/TST_EXP_FAIL errno or invariant checks; notable reported messages include `bad socket file descriptor`; `Child killed by expected signal`; `sendmmsg() failed`.
