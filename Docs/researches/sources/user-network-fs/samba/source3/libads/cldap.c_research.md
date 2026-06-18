# sources/user-network-fs/samba/source3/libads/cldap.c

## Purpose
`cldap.c` performs ADS CLDAP netlogon pings against a domain controller on UDP/389 and exposes a NETLOGON_NT_VERSION_5EX response helper.

## Important APIs and Functions
The static `ads_cldap_netlogon` builds a `tsocket_address` from a `sockaddr_storage`, calls `netlogon_pings` with a domain, requested ntversion, required flags, and timeout, and returns the first response. `ads_cldap_netlogon_5` requests `NETLOGON_NT_VERSION_5 | NETLOGON_NT_VERSION_5EX` and copies out `NETLOGON_SAM_LOGON_RESPONSE_EX`.

## Control Flow and State
The helper always targets LDAP port 389, asks for one wanted server, and uses a timeout of at least three seconds or half the LDAP timeout. It fails if no response arrives or if the response version is not 5EX. It has no durable state.

## Dependencies and Integration Points
It depends on CLDAP/netlogon client libraries, `tsocket`, loadparm ping protocol and timeout, NTSTATUS mapping, and generated netlogon NDR structures. It is used by ADS DC discovery and site/KDC selection logic.

## Risks and Test Signals
Network behavior and firewall drops dominate failures. `ads_cldap_netlogon_5` shallow-copies fields from a talloc-owned response; callers must ensure referenced subfields remain valid or understand generated struct ownership. Tests should cover address conversion failure, timeout/no response, required-flag mismatch, wrong ntversion, IPv4/IPv6 addresses, and successful pdc/domain response extraction.
