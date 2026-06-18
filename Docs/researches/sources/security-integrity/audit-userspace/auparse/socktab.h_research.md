<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/socktab.h -->
# sources/security-integrity/audit-userspace/auparse/socktab.h

## Purpose
Maps legacy multiplexed `socketcall` operation ids to socket operation names.

## Important APIs, types, and functions
The `_S` table names operations such as socket, bind, connect, listen, accept, send/recv variants, shutdown, getsockopt/setsockopt, accept4, recvmmsg, and sendmmsg.

## Control flow
Generated `sock_i2s` is used by `print_socketcall` and `print_syscall` for legacy `socketcall` syscall records.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Uses Linux net syscall constants and integrates with libaudit syscall-name resolution.

## Risks and test signals
Risks are legacy architecture differences and missing multiplexed operations. Tests should verify common operation names and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/socktab.h -->
