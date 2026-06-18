
# sources/security-integrity/ima-evm-utils/tests/kernel/test_mmap.c

## Purpose
`test_mmap.c` is a small helper program for testing IMA `MMAP_CHECK` and `MMAP_CHECK_REQPROT` hooks under different mmap and mprotect scenarios.

## Important APIs, Types, And Functions
`main()` accepts a file path and optional mode: `read_implies_exec`, `exec_on_writable`, `exec*`, or `mprotect`. It uses `personality(READ_IMPLIES_EXEC)`, `stat()`, `open()`, `mmap()`, `mprotect()`, and `munmap()`. Return codes distinguish setup errors (`1`) from expected test-condition denials (`2`).

## Control Flow
The program validates the file, optionally sets personality, optionally creates a writable shared mapping, opens the file read-only, maps it with `PROT_READ` and optionally `PROT_EXEC`, handles expected denial cases, optionally calls `mprotect(PROT_EXEC)`, unmaps, and exits with the classification code.

## State And Persistence
It does not persist data, but may temporarily create mappings and alter process personality. It opens the target file read-only except for the writable mapping scenario.

## Dependencies And Integration Points
Kernel tests use it to trigger IMA mmap hooks and check whether policy/appraisal blocks execution mapping as expected.

## Risks
Behavior is kernel-policy dependent. `personality(READ_IMPLIES_EXEC)` affects the current process only. File size zero or unusual files may affect mmap behavior.

## Test Signals
The helper's exit code is the primary signal for `mmap_check.test`: `0` for allowed mapping, `2` for expected policy denial, `1` for setup failure.
