# sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/socketpair01.c

## Purpose
Verify that socketpair(2) fails and set proper errno - EAFNOSUPPORT on invalid domain - EINVAL on
invalid type - EPROTONOSUPPORT on raw open as non-root - EFAULT on bad aligned pointer - EFAULT on
bad unaligned pointer - EOPNOTSUPP on UDP socket - EPROTONOSUPPORT on TCP dgram - EOPNOTSUPP on TCP
socket - EPROTONOSUPPORT on ICMP stream Also test creating UNIX domain dgram.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socketpair`; types `struct test_case_t`, `struct
tst_test`; safe wrappers `SAFE_CLOSE`; harness APIs `tst_test`, `TEST`, `tst_res`, `tst_strerrno`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `verify_socketpair`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: invalid-address tests can expose architecture-specific fault delivery.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`; expected errno/status values
`EAFNOSUPPORT`, `EINVAL`, `EPROTONOSUPPORT`, `EFAULT`, `EOPNOTSUPP`.
