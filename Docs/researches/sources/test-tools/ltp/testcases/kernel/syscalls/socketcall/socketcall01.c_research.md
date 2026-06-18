# sources/test-tools/ltp/testcases/kernel/syscalls/socketcall/socketcall01.c

## Purpose
Basic test for the socketcall(2) raw syscall. Test creating TCP, UDP, raw socket and unix domain
dgram.

## Important APIs, types, and functions
Important interfaces include syscall/library calls `socketcall`; types `struct test_case_t`, `struct
tst_test`; constants/macros `AF_INET`; safe wrappers `SAFE_CLOSE`; harness APIs `tst_test`, `TEST`,
`tst_syscall`, `tst_res`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test`, `.tcnt`,
`.needs_root`. Local functions include `verify_socketcall`.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges, `lapi/syscalls.h` compatibility
wrappers, Linux UAPI headers. The file is built by the syscall directory Makefile and executed as
part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage;
obsolete or direct syscall paths may be absent or emulated differently on newer architectures.

## Test signals
LTP result macros `TPASS`, `TFAIL`, `TTERRNO`, `TERRNO`.
