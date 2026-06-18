# sources/test-tools/ltp/testcases/kernel/syscalls/socketpair/socketpair02.c

## Purpose
This LTP test source exercises `socketpair` syscall behavior in `socketpair02.c`.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socket`, `socketpair`; types `struct tcase`,
`struct tst_test`; safe wrappers `SAFE_FCNTL`, `SAFE_CLOSE`; harness APIs `tst_test`, `TEST`,
`tst_brk`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.cleanup`, `.test`, `.tcnt`.
Local functions include `verify_socketpair`, `cleanup`.

## State and persistence behavior
The test opens kernel socket descriptors and closes them in test or cleanup paths. State is scoped
to the LTP process tree unless a privileged syscall changes host-visible kernel state before
cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/fcntl.h` compatibility wrappers. The file
is built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`.
