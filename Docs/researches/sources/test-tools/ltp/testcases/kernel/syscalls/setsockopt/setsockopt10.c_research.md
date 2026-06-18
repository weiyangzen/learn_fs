# sources/test-tools/ltp/testcases/kernel/syscalls/setsockopt/setsockopt10.c

## Purpose
Reproducer for CVE-2023-0461 which is an exploitable use-after-free in a TLS socket. In fact it is
exploitable in any User Level Protocol (ULP) which does not clone its context when accepting a
connection. Because it does not clone the context, the child socket which is created on accept has a
pointer to the listening socket's context. When the child is closed the parent's context is freed
while it still has a reference to it. TLS can only be added to a socket which is connected. Not
listening or disconnected, and a connected socket can not be set to listening. So we have to connect
the socket, add TLS, then disconnect, then set it to listening. To my knowledge, setting a socket
from open. CVE/regression focus: CVE-2023-0461. Referenced kernel commit ids include
`2c02d41d71f90a5168391b6a5f2954112ba2307c`, `2c02d41d71f90`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setsockopt`, `connect`; types `struct
tls12_crypto_info_aes_gcm_128`, `struct sockaddr_in`, `struct sockaddr`, `struct tst_test`, `struct
tst_tag`; constants/macros `AF_UNSPEC`, `AF_INET`, `SOL_TCP`, `SOL_TLS`; safe wrappers `SAFE_CLOSE`,
`SAFE_SOCKET`, `SAFE_BIND`, `SAFE_LISTEN`, `SAFE_ACCEPT`, `SAFE_FORK`, `SAFE_CONNECT`,
`SAFE_SETSOCKOPT`; harness APIs `tst_test`, `tst_checkpoint`, `tst_net`, `tst_safe_net`,
`tst_taint`, `tst_init_sockaddr_inet`, `tst_res`, `TEST`, `tst_brk`, `tst_reap_children`,
`tst_flush`, `tst_tag`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`, `.forks_child`. Local functions include `setup`, `cleanup`, `child`, `run`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths; uses child
processes and wait/exit status as observable state. State is scoped to the LTP process tree unless a
privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, kernel config gates "CONFIG_TLS",
`lapi/socket.h` compatibility wrappers, Linux UAPI headers. The file is built by the syscall
directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: security regression coverage may intentionally exercise vulnerable kernel paths and often
reports success by not crashing; missing kernel options cause configuration skips rather than
failures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TCONF`, `TINFO`, `TTERRNO`, `TERRNO`; expected
errno/status values `EINVAL`, `ENOENT`, `EOPNOTSUPP`; regression tags for CVE-2023-0461.
