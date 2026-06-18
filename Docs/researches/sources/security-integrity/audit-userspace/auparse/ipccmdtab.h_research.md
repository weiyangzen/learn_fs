<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipccmdtab.h -->
# sources/security-integrity/audit-userspace/auparse/ipccmdtab.h

## Purpose
Maps System V IPC flag bits to names used when interpreting shared-memory creation flags.

## Important APIs, types, and functions
The `_S` entries cover `IPC_CREAT`, `IPC_EXCL`, and `IPC_NOWAIT`.

## Control flow
Generated table data is used by `interpret.c:print_shmflags`, which combines IPC command flags, SHM mode flags, and permission bits.

## State and persistence behavior
Static table data only.

## Dependencies and integration points
Based on Linux IPC headers; integrated with `shm_modetab.h` and mode rendering.

## Risks and test signals
Risks are missing IPC flags or octal-mask mistakes. Tests should validate combined flag and permission output for `shmget`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipccmdtab.h -->
