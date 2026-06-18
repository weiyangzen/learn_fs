# sources/test-tools/ltp/testcases/kernel/syscalls/socket/socket01.c

## Purpose
Test creating TCP, UDP, and Unix doman dgram sockets with socket() syscall. Also verify that
socket() fails and set proper errno - EAFNOSUPPORT on invalid domain - EINVAL on invalid type -
EPROTONOSUPPORT on raw open as non-root - EPROTONOSUPPORT on UDP stream - EPROTONOSUPPORT on TCP
dgram - EPROTONOSUPPORT on ICMP stream.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socket`; types `struct test_case_t`, `struct
tst_test`; safe wrappers `SAFE_CLOSE`; harness APIs `tst_test`, `TEST`, `tst_res`, `tst_strerrno`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `verify_socket`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values
`EAFNOSUPPORT`, `EINVAL`, `EPROTONOSUPPORT`.
