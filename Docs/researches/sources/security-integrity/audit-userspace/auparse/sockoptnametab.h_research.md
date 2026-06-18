<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/sockoptnametab.h -->
# sources/security-integrity/audit-userspace/auparse/sockoptnametab.h

## Purpose
Maps `SOL_SOCKET` option ids to symbolic option names.

## Important APIs, types, and functions
The `_S` table covers classic socket options, timestamping, BPF attach/detach, busy poll, cookies, buffer locks, memory reservation, PIDFD options, and PPC-specific remapped entries.

## Control flow
Generated `sockoptname_i2s` is called by `interpret.c:print_sock_opt_name`; PPC/PPC64 values in a specific range are adjusted by adding 100 before lookup.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks asm-generic socket headers and architecture differences. Selected by `print_a2` when socket option level is `SOL_SOCKET`.

## Risks and test signals
Risks are architecture remap errors, new socket options, and level confusion. Tests should cover common options, PPC-adjusted values, new high ids, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/sockoptnametab.h -->
