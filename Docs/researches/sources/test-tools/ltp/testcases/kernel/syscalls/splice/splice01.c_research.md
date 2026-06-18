# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice01.c

## Purpose
This test case will verify basic function of splice added by kernel 2.6.17 or up.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`; safe wrappers
`SAFE_OPEN`, `SAFE_READ`, `SAFE_CLOSE`, `SAFE_PIPE`, `SAFE_WRITE`, `SAFE_WRITE_ALL`; harness APIs
`tst_test`, `tst_res`, `tst_brk`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`, `.needs_tmpdir`. Local functions include `check_file`, `splice_test`, `setup`,
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
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TERRNO`.
