# sources/test-tools/ltp/testcases/kernel/syscalls/shutdown/shutdown02.c

## Purpose
This test verifies the following shutdown() errors: - EBADF sockfd is not a valid file descriptor -
EINVAL An invalid value was specified in how - ENOTCONN The specified socket is not connected -
ENOTSOCK The file descriptor sockfd does not refer to a socket.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `shutdown`; types `struct sockaddr_in`, `struct
tcase`, `struct sockaddr`, `struct tst_test`, `struct tst_buffers`; constants/macros `AF_INET`; safe
wrappers `SAFE_OPEN`, `SAFE_SOCKET`, `SAFE_BIND`, `SAFE_CLOSE`; harness APIs `tst_test`,
`TST_EXP_FAIL`, `tst_buffers`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `run`, `setup`, `cleanup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
expected errno/status values `EBADF`, `EINVAL`, `ENOTCONN`, `ENOTSOCK`.
