# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice09.c

## Purpose
Test for splicing to /dev/zero and /dev/null these two devices discard all data written to them. The
support for splicing to /dev/zero was added in: 1b057bd800c3 ("drivers/char/mem: implement splice()
for /dev/zero, /dev/full"). Referenced kernel commit ids include `1b057bd800c3`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`; safe wrappers
`SAFE_OPEN`, `SAFE_PIPE`, `SAFE_WRITE`, `SAFE_CLOSE`; harness APIs `tst_test`, `tst_res`,
`TST_EXP_POSITIVE`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `verify_splice`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness. The file is built by the syscall directory
Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TFAIL`, `TINFO`.
