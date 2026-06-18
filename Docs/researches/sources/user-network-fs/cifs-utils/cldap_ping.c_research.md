<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cldap_ping.c -->
# sources/user-network-fs/cifs-utils/cldap_ping.c

## Purpose

`cldap_ping.c` sends an Active Directory CLDAP ping to domain controllers to learn the client's site name, allowing `resolve_host.c` to prefer site-local DC addresses for DFS/domain mounts.

## Important APIs, Types, and Functions

Important functions are `parse_ber_size`, `read_dns_string`, `generate_cldap_query`, `extract_netlogon_section`, `netlogon_get_client_site`, and `cldap_ping`. It uses ASN.1 writer helpers, resolver `dn_expand`, UDP sockets, and CLDAP/LDAP/NetLogon constants.

## Control Flow

`cldap_ping` creates a UDP socket, builds an LDAP search request for `DnsDomain=<domain>` and `NtVer=\x06\x00\x00\x00`, sends it to port 389, receives a response, extracts the `NetLogon` octet string, and parses the `NETLOGON_SAM_LOGON_RESPONSE_EX` variable DNS-compressed strings until the client site name is reached. `CLDAP_PING_TRYNEXT` tells callers to try another DC; other negative values are fatal parse or network errors.

## State and Persistence Behavior

All state is transient: socket, ASN.1 buffer, response buffer, and caller-provided `site_name`. It does not persist data.

## Dependencies and Integration Points

It depends on libtalloc, libresolv, sockets, `data_blob.h`, `asn1.h`, and `cldap_ping.h`. `resolve_host.c` calls it while processing AD SRV records.

## Risks and Edge Cases

The BER parser is manually pointer-based and has limited bounds enforcement after each step. `generate_cldap_query` returns an `ASN1_DATA` that is not freed if socket option or send setup fails after allocation. DNS-compressed NetLogon strings depend on `dn_expand` offsets and a caller-provided `MAXCDNAME` buffer. The function assumes AD additional records contain usable IPs.

## Test Signals

Tests should use captured CLDAP responses and malformed BER/NetLogon buffers, verify `CLDAP_PING_TRYNEXT` on pause responses, cover IPv4/IPv6 socket paths, and run resolver integration against a controlled AD-like DNS/CLDAP fixture.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cldap_ping.c -->
