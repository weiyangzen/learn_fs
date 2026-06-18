# sources/test-tools/ltp/testcases/kernel/syscalls/setrlimit/setrlimit04.c

## Purpose
Attempt to run a trivial binary with stack < 1MB. Early patches for stack guard gap caused that gap
size was contributing to stack limit. This caused failures for new processes (E2BIG) when ulimit was
set to anything lower than size of gap. Kernel commit 1be7107fbe18 ("mm: largerstack guard gap,
between vmas") from v4.12 sets default gap size to 1M (for systems with 4k pages), so let's set
stack limit to 512kB and confirm we can still run some trivial binary. Referenced kernel commit ids
include `1be7107fbe18`.

## Important APIs, types, and functions
Important interfaces include types `struct rlimit`, `struct tst_test`; constants/macros
`RLIMIT_STACK`; safe wrappers `SAFE_SETRLIMIT`, `SAFE_FORK`, `SAFE_EXECLP`, `SAFE_WAITPID`; harness
APIs `tst_test`, `tst_res`, `tst_strstatus`.

## Control flow
The modern LTP harness drives execution through `struct tst_test` with `.test_all`, `.test`,
`.forks_child`, `.needs_root`. Local functions include `test_setrlimit`.

## State and persistence behavior
The test uses child processes and wait/exit status as observable state; changes resource limits in
the current process or child process. State is scoped to the LTP process tree unless a privileged
syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies include modern `tst_test` LTP harness, root privileges. The file is built by the
syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: privilege assumptions can produce `TCONF`/`TBROK` instead of meaningful syscall coverage.

## Test signals
LTP result macros `TPASS`, `TFAIL`; expected errno/status values `E2BIG`.
