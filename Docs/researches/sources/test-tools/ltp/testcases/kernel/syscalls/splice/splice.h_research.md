# sources/test-tools/ltp/testcases/kernel/syscalls/splice/splice.h

## Purpose
This header provides `get_max_limit()`, a shared helper for splice tests that caps default pipe test
sizes against `/proc/sys/fs/pipe-max-size` or `/proc/sys/fs/pipe-max-pages` when those kernel
tunables exist.

## Important APIs, types, and functions
Important interfaces include safe wrappers `SAFE_FILE_SCANF`; harness APIs `tst_safe_file_ops`,
`tst_minmax`.

## Control flow
This helper/header is consumed by neighboring tests at compile time; it provides compatibility
definitions and small wrappers rather than a standalone runtime entry point.

## State and persistence behavior
The test does not persist data beyond normal LTP build/runtime artifacts. State is scoped to the LTP
process tree unless a privileged syscall changes host-visible kernel state before cleanup.

## Dependencies and integration points
Dependencies are the C library, Linux syscall ABI, and the LTP build/runtime harness. The file is
built by the syscall directory Makefile and executed as part of the LTP kernel syscall suite.

## Risks and edge cases
Key risks: main risk is environmental: unsupported syscall, unexpected errno, or cleanup not running
after a broken assertion.

## Test signals
Successful completion of the LTP binary is the main signal, with failures emitted through the
harness.
