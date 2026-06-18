# sources/user-network-fs/samba/source4/torture/ldap/netlogon.c

## Purpose

`netlogon.c` tests LDAP and CLDAP netlogon ping behavior. It validates netlogon response semantics across NT version flags, user/domain/GUID/account-control inputs, server-type flags, extra RootDSE attributes with netlogon, no-`NtVer` compatibility, and both CLDAP and LDAP ping transports.

## Important APIs, Types, and Functions

- `struct cldap_netlogon` is the local request/response shape used by generic test functions.
- `request_netlogon_t` and `request_rootdse_t` abstract CLDAP/LDAP request backends.
- `test_ldap_netlogon()` exercises many netlogon filter combinations and expected response commands.
- `test_ldap_netlogon_flags()` prints decoded `server_type` flags.
- `tcp_ldap_rootdse()` maps a raw LDAP base search into `struct cldap_search`-style output.
- `udp_ldap_rootdse()` delegates to `cldap_search()`.
- `test_netlogon_extra_attrs()` verifies netlogon plus additional attributes and wildcard restrictions.
- `test_netlogon_huawei()` covers clients that omit `NtVer` and expects NT5 response.
- `test_netlogon_ping()` adapts `netlogon_pings()` to `struct cldap_netlogon`.
- `torture_netlogon_tcp()`, `torture_netlogon_udp()`, and `torture_netlogon_ping()` are suite entry points.

## Control Flow

The generic netlogon flow starts with a minimal request to learn baseline domain data, scans all 0-255 version values and individual version bits for successful responses, then asserts detailed behavior for null users, known/unknown users, NT5 versus NT5EX response commands, GUID-only searches, incorrect GUID/domain combinations, account-control variations, and field consistency against the baseline response.

TCP and UDP RootDSE tests use the same extra-attribute checks through backend adapters. TCP opens a raw LDAP connection and parses entry/done replies; UDP initializes a CLDAP socket. The ping test resolves the host to an IP, then runs the generic netlogon and flag tests twice through `netlogon_pings()`: once with `CLIENT_NETLOGON_PING_CLDAP` and once with `CLIENT_NETLOGON_PING_LDAP`.

## State and Persistence Behavior

The tests are read-only. They create transient LDAP/CLDAP sockets, parse netlogon blobs, and hold response pointers under request memory contexts.

## Dependencies and Integration Points

Dependencies include `libcli/cldap`, raw LDAP client structures, `ldap_ndr` helpers, `netlogon_ping`, NDR netlogon types, DNS/NetBIOS resolution, DOM SID/GUID parsing, `tsocket`, and loadparm DNS domain/client ping protocol settings. The entry points are registered in `common.c`.

## Risks and Edge Cases

The test encodes many Windows-compatible netlogon expectations, including UNC versus non-UNC PDC names, response command variants, wildcard filter rejection, and no-`NtVer` behavior. Small server-side compatibility changes can break strict assertions. Some status checks inspect output fields even after `NT_STATUS_NOT_FOUND`, so response initialization matters.

## Test Signals

Strong signals are correct status codes for valid and invalid domain/GUID inputs, expected `LOGON_SAM_LOGON_*` command values, stable forest/domain/PDC/site fields, correct extra-attribute behavior, `NETLOGON_NT_VERSION_5` for no-`NtVer`, and successful generic tests over both LDAP and CLDAP ping protocols.
