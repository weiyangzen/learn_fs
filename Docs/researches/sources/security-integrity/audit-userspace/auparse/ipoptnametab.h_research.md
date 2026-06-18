<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipoptnametab.h -->
# sources/security-integrity/audit-userspace/auparse/ipoptnametab.h

## Purpose
Maps IPv4 socket option ids to symbolic names.

## Important APIs, types, and functions
The `_S` table covers IP TOS/TTL/options/MTU/error/multicast controls, transparent/freebind, local port range, protocol selection, and iptables socket option constants.

## Control flow
Generated `ipoptname_i2s` is called by `interpret.c:print_ip_opt_name` when `print_a2` sees a socket option level of `IPPROTO_IP`.

## State and persistence behavior
Static lookup table only.

## Dependencies and integration points
Tracks Linux IPv4 and netfilter headers. Integrated with `getsockopt`/`setsockopt` argument interpretation.

## Risks and test signals
Risks are missing newer options and wrong socket level context. Tests should cover common option names, netfilter option ids, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ipoptnametab.h -->
