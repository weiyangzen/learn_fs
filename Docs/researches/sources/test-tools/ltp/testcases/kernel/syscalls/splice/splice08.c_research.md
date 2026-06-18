# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice08.c

## Purpose
Test for splicing from /dev/zero and /dev/full. The support for splicing from /dev/zero and
/dev/full was removed in: c6585011bc1d ("splice: Remove generic_file_splice_read()") And added back
in: 1b057bd800c3 ("drivers/char/mem: implement splice() for /dev/zero, /dev/full"). Referenced
kernel commit ids include `c6585011bc1d`, `1b057bd800c3`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`; safe wrappers
`SAFE_PIPE`, `SAFE_READ`, `SAFE_CLOSE`, `SAFE_OPEN`; harness APIs `tst_test`, `TST_EXP_POSITIVE`,
`tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`. Local functions include `test_splice`, `verify_splice`, `setup`, `cleanup`.

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
LTP result macros `TPASS`, `TFAIL`, `TINFO`.
