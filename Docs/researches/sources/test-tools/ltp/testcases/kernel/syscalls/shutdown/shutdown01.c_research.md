# sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/shutdown01.c

## Purpose
This test verifies the following shutdown() functionalities: - SHUT_RD should enable send() ops but
disable recv() ops - SHUT_WR should enable recv() ops but disable send() ops - SHUT_RDWR should
disable both recv() and send() ops.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `send`, `recv`, `shutdown`; types `struct tcase`,
`struct sockaddr_un`, `struct sockaddr`, `struct tst_test`, `struct tst_buffers`; constants/macros
`AF_UNIX`; safe wrappers `SAFE_SOCKET`, `SAFE_BIND`, `SAFE_LISTEN`, `SAFE_CLOSE`, `SAFE_UNLINK`,
`SAFE_FORK`, `SAFE_CONNECT`, `SAFE_RECV`, `SAFE_SEND`; harness APIs `tst_test`, `tst_safe_net`,
`tst_res`, `TST_EXP_PASS`, `TST_EXP_FAIL`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.test`, `.tcnt`,
`.forks_child`. Local functions include `run_server`, `start_test`, `run`, `setup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths; uses child
processes and wait/exit status as observable state. State is scoped to the LTP process tree unless a
privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TINFO`; expected errno/status values `EWOULDBLOCK`, `EPIPE`.
