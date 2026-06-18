<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/socktypetab.h -->
# sources/security-integrity/audit-userspace/auparse/socktypetab.h

## Purpose
Maps socket type ids to symbolic socket type names.

## Important APIs, types, and functions
The `_S` table includes stream, datagram, raw, RDM, seqpacket, DCCP, and packet socket types.

## Control flow
Generated `sock_type_i2s` is called by `interpret.c:print_socket_type`, which masks low bits before lookup.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks Linux net/socket headers. Used for `socket` syscall argument `a1`.

## Risks and test signals
Risks are masked-out modifier flags and new socket types. Tests should cover known types, type values with flags, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/socktypetab.h -->
