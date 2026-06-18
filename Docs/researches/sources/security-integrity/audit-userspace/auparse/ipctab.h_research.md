<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipctab.h -->
# sources/security-integrity/audit-userspace/auparse/ipctab.h

## Purpose
Maps multiplexed `ipc` syscall operation numbers to operation names.

## Important APIs, types, and functions
The `_S` table names semaphore, message queue, shared memory, and DIPC operation ids such as `semop`, `msgsnd`, `shmat`, and `shmctl`.

## Control flow
Generated `ipc_i2s` is called by `print_ipccall` and `print_syscall` when interpreting legacy `ipc` syscall records.

## State and persistence behavior
Static compile-time data only.

## Dependencies and integration points
Uses constants duplicated in `interpret.c` because some platform headers are unreliable. Integrated with libaudit syscall-name resolution.

## Risks and test signals
Risks are architecture/header mismatches and legacy multiplexing differences. Tests should check named IPC operations and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipctab.h -->
