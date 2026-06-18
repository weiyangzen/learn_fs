# sources/user-network-fs/samba/source4/lib/socket/access.c

## Purpose

`access.c` checks whether an accepted socket connection should be allowed for a Samba service based on allow and deny lists. It adapts tcp_wrappers-style access matching to Samba socket contexts.

## Important APIs, Types, and Functions

`socket_check_access()` is the exported decision function. Internal `only_ipaddrs_in_list()` determines whether host name lookups can be skipped because allow/deny tokens are IP addresses, network/netmask pairs, or special strings.

## Control Flow

If both allow and deny lists are empty, access is allowed immediately. Otherwise the function allocates a talloc context, fetches the peer address from the socket, optionally resolves the peer name when any list contains non-IP tokens, and calls `allow_access(deny_list, allow_list, name, addr->addr)`. It logs allowed connections at debug level 2 and denied connections at level 0.

## State and Persistence Behavior

The function has no persistent state. It allocates temporary address/name data and frees it before returning. Its only side effect is logging.

## Dependencies and Integration Points

It depends on Samba socket APIs, network system headers, IP address helpers, and `lib/util/access.h` matching logic. Services use it after accepting a socket and before processing service-specific protocols.

## Risks and Edge Cases

When peer address lookup fails, access is denied. Hostname resolution is skipped only if both lists are IP-only, so DNS delays or failures can affect connection setup when names are configured. Network/netmask tokens are treated as IP-only if they contain `/`, even if malformed; actual validation happens later in `allow_access()`.

## Test Signals

Tests should cover empty lists, allow-only, deny-only, deny overriding allow, `ALL`/`EXCEPT`/`FAIL`, IP-only bypass without reverse lookup, hostname-based rules, unknown peer address failure, and IPv4/IPv6 network tokens.

Source-read signal: reviewed complete local file (129 lines).
