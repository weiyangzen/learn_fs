# sources/test-tools/ltp/testcases/kernel/syscalls/setuid/setuid01.c

## Purpose
Verify that setuid(2) returns 0 and effective uid has been set successfully as a normal or super
user.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `setuid`; types `struct tst_test`; harness APIs
`tst_test`, `TST_EXP_PASS`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`. Local
functions include `verify_setuid`.

## State and persistence behavior
The test changes process credentials for the running process or child. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: compatibility-mode behavior depends on architecture, compiler flags, and kernel ABI
support.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.
