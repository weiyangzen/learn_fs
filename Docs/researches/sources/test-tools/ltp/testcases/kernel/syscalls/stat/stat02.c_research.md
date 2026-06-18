# sources/test-tools/ltp/testcases/kernel/syscalls/stat/stat02.c

## Purpose
Now check to see if the number of bytes written was the same as the number of bytes in the file.

## Important APIs, types, and functions
Important interfaces include types `struct test_case`, `struct stat`, `struct tst_test`; safe
wrappers `SAFE_OPEN`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `SAFE_CLOSE`, `SAFE_STAT`, `SAFE_UNLINK`,
`SAFE_MALLOC`; harness APIs `tst_test`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test`, `.tcnt`, `.needs_tmpdir`. Local functions include `verify`, `verify_stat_size`, `setup`,
`cleanup`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, temporary directory support. The file is built
by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`.
