# sources/test-tools/ltp/testcases/kernel/syscalls/statmount/statmount.h

## Purpose
This header provides compatibility definitions and wrappers for the new `statmount()` syscall so the
adjacent tests can build across libc and kernel header versions.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `statmount`; types `struct statmount`;
constants/macros `STATMOUNT_H`; safe wrappers `SAFE_FOPEN`; harness APIs `tst_test`,
`tst_safe_stdio`, `tst_syscall`, `tst_brk`.

## Control flow
This helper/header is consumed by neighboring tests at compile time; it provides compatibility
definitions and small wrappers rather than a standalone runtime entry point.

## State and persistence behavior
The test mutates mount namespace or mount table state and must clean it up. State is scoped to the
LTP process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, `lapi/syscalls.h` compatibility wrappers. The
file is built by the syscall directory Makefile and executed as part of the LTP kernel syscall
suite.

## Risks and edge cases
Key risks: mount namespace, filesystem type, and kernel version differences affect expected fields;
obsolete or direct syscall paths may be absent or emulated differently on newer architectures.

## Test signals
LTP result macros `TBROK`.
