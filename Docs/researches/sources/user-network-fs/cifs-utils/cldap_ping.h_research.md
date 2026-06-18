<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cldap_ping.h -->
# sources/user-network-fs/cifs-utils/cldap_ping.h

## Purpose

`cldap_ping.h` declares the CLDAP ping API and error codes used by the host resolver.

## Important APIs, Types, and Functions

The header defines `CLDAP_PING_NETWORK_ERROR`, `CLDAP_PING_TRYNEXT`, `CLDAP_PING_PARSE_ERROR_LDAP`, `CLDAP_PING_PARSE_ERROR_NETLOGON`, and `cldap_ping(char *domain, sa_family_t family, void *addr, char *site_name)`.

## Control Flow

Callers pass a domain, address family, raw address pointer, and `MAXCDNAME`-sized output buffer. `CLDAP_PING_TRYNEXT` is explicitly recoverable by trying another DC; other negative errors are fatal for the current resolver attempt.

## State and Persistence Behavior

The header defines no state. `site_name` is caller-owned output.

## Dependencies and Integration Points

It requires socket address family types from system headers included by consumers. `resolve_host.c` is the direct consumer.

## Risks and Edge Cases

The API uses `void *addr` and mutable `char *domain`, so type safety is caller-enforced. The comment requiring `site_name` to be `MAXCDNAME` sized is not encoded in the type.

## Test Signals

Compile tests and resolver tests should verify error-code handling and buffer-size assumptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/cldap_ping.h -->
