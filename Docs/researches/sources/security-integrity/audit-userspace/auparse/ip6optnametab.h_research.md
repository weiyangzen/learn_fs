<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ip6optnametab.h -->
# sources/security-integrity/audit-userspace/auparse/ip6optnametab.h

## Purpose
Maps IPv6 socket option numbers to symbolic names for `getsockopt`/`setsockopt` interpretation.

## Important APIs, types, and functions
The `_S` table includes legacy `IPV6_2292*`, multicast membership controls, packet info/hop/destination/routing options, firewall revision constants, flowlabel, transparency, and original-destination options.

## Control flow
Generated `ip6optname_i2s` is called by `interpret.c:print_ip6_opt_name` when syscall context says socket level is `IPPROTO_IPV6`.

## State and persistence behavior
Static lookup table only.

## Dependencies and integration points
Tracks Linux IPv6, netfilter IPv6, and multicast route headers. Integration depends on `print_a2` correctly reading `id->a1` socket option level.

## Risks and test signals
Risks are Linux header drift and context misclassification. Tests should cover known IPv6 options, unknown fallback, and end-to-end `setsockopt` with level `IPPROTO_IPV6`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ip6optnametab.h -->
