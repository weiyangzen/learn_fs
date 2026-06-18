# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice04.c

## Purpose
This LTP test source exercises `splice` syscall behavior in `splice04.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `splice`; types `struct tst_test`, `struct
tst_option`; safe wrappers `SAFE_MALLOC`, `SAFE_PIPE`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `SAFE_READ`,
`SAFE_CLOSE`; harness APIs `tst_test`, `tst_parse_int`, `tst_brk`, `tst_res`, `tst_option`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.setup`, `.cleanup`,
`.test_all`, `.test`. Local functions include `setup`, `cleanup`, `pipe_pipe`.

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
LTP result macros `TPASS`, `TFAIL`, `TBROK`, `TINFO`, `TERRNO`.
