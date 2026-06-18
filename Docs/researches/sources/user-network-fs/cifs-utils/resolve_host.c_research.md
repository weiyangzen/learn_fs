<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/resolve_host.c -->
# sources/user-network-fs/cifs-utils/resolve_host.c

## Purpose

`resolve_host.c` resolves a hostname to a comma-separated bounded list of IPv4/IPv6 address strings for mount and credential helpers. For AD/DFS-like domains with multiple DC addresses, it can use DNS SRV records plus CLDAP ping to prioritize domain controllers in the client's site.

## Important APIs, Types, and Functions

The public function is `resolve_host(const char *host, char *addrstr)`. It uses `getaddrinfo`, `inet_ntop`, resolver APIs `res_init`, `res_query`, `ns_initparse`, `ns_parserr`, `ns_msg_count`, DNS record types `A`, `AAAA`, and `SRV`, and `cldap_ping`.

## Control Flow

The function first calls `getaddrinfo`, filters TCP IPv4/IPv6 results, limits them to `MAX_ADDRESSES`, and appends printable addresses to `addrstr`. If more than one IPv4 or IPv6 address exists, it queries `_ldap._tcp.dc._msdcs.<host>` for global DC SRV data. With multiple DCs, it pings additional A/AAAA addresses to learn `site_name`, queries `_ldap._tcp.<site>._sites.dc._msdcs.<host>`, rebuilds `addrstr` with site-local addresses first, then appends non-duplicate global addresses up to the limit.

## State and Persistence Behavior

The function is stateless apart from resolver library state initialized by `res_init`. Output is caller-owned `addrstr`. No disk state is written.

## Dependencies and Integration Points

It depends on libc name resolution, libresolv, `mount.h` exit codes, `util.h`, `cldap_ping.h`, and `resolve_host.h`. It is used by `mount.cifs`, `cifscreds`, and `pam_cifscreds`.

## Risks and Edge Cases

The initial comma insertion checks `addr == addrlist`, but skipped leading `addrinfo` entries can leave `addrstr` uninitialized when the first usable address is not the first list node. Duplicate detection uses substring search with separator checks. DNS/CLDAP errors in the optimization path mostly fall through to returning the original address list, but `rc` must remain meaningful. Buffer sizing uses `MAX_ADDR_LIST_LEN`, which must account for IPv6 scope ids and commas.

## Test Signals

Tests should cover IPv4, IPv6 with scope id, non-TCP addrinfo entries before usable entries, more than `MAX_ADDRESSES`, DNS failures, AD site-local prioritization with mocked resolver/CLDAP data, duplicate suppression, and callers' handling of `EX_USAGE` versus `EX_SYSERR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/resolve_host.c -->
