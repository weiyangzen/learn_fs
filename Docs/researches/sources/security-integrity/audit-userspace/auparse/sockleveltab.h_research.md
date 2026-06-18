<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/sockleveltab.h -->
# sources/security-integrity/audit-userspace/auparse/sockleveltab.h

## Purpose
Maps socket option level numbers to symbolic `SOL_*` names.

## Important APIs, types, and functions
The `_S` table covers IP/TCP/UDP/IPV6/ICMPV6 and many protocol levels including packet, netlink, Bluetooth, TLS, XDP, MPTCP, MCTP, SMC, and VSOCK.

## Control flow
Generated `socklevel_i2s` is a fallback in `interpret.c:print_sock_opt_level` when libc protocol lookup does not provide a name and the level is not `SOL_SOCKET`.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks Linux socket headers and complements `getprotobynumber`. It feeds `getsockopt`/`setsockopt` level interpretation.

## Risks and test signals
Risks are overlap with protocol database names, new levels, and platform differences. Tests should cover `SOL_SOCKET`, protocol-db levels, table-only levels, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/sockleveltab.h -->
