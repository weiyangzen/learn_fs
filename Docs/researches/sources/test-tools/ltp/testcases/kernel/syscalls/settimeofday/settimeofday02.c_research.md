# sources/test-tools/ltp/testcases/kernel/syscalls/settimeofday/settimeofday02.c

## Purpose
This LTP test source exercises `settimeofday` syscall behavior in `settimeofday02.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `settimeofday`; types `struct tcase`, `struct
timeval`, `struct tst_test`, `struct tst_cap`; harness APIs `tst_capability`, `tst_test`, `tst_res`,
`TST_EXP_FAIL`, `tst_cap`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`. Local
functions include `verify_settimeofday`.

## State and persistence behavior
The test may alter system clock state, so setup/cleanup must preserve host time expectations. State
is scoped to the LTP process tree unless a privileged syscall changes host-visible kernel state
before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/syscalls.h` compatibility wrappers. The
file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TINFO`; expected errno/status values `EINVAL`, `EPERM`.
