# sources/user-network-fs/samba/source3/libads/netlogon_ping.c

## Purpose

`netlogon_ping.c` sends NetLogon discovery pings over CLDAP, LDAP, LDAPS, or LDAP StartTLS and returns parsed `netlogon_samlogon_response` objects. It is the async engine used by ADS DC discovery to find usable domain controllers.

## Important APIs, Types, and Functions

`check_cldap_reply_required_flags` validates DC capability flags. Public APIs are `netlogon_pings_send`, `netlogon_pings_recv`, and synchronous `netlogon_pings`. Internal request families include `ldap_netlogon_send/recv` for LDAP-family transports, `cldap_netlogon_ping_send/recv` for CLDAP, `netlogon_ping_send/recv` for one server, and `netlogon_pings_next/done` for staggered multi-server orchestration. State structs include `ldap_netlogon_state`, `cldap_netlogon_ping_state`, `netlogon_ping_state`, and `netlogon_pings_state`.

## Control Flow

The multi-ping sender builds an LDAP filter from `netlogon_ping_filter` fields (`NtVer`, domain, account control, domain SID/GUID, host, user), starts requests to the first `wanted_servers`, then schedules additional sends every 100 ms until all candidates are in flight. CLDAP uses `cldap_search_send` against UDP/389 for the `NetLogon` attribute. LDAP-family pings TCP-connect to 389 or 636, optionally perform StartTLS or direct TLS setup without peer verification in this discovery path, run a base search for `netlogon`, then parse the returned blob.

Each completed response is parsed and filtered: paused responses are rejected, `required_flags` must be present, and successful responses are stored at the server's original index. The aggregate request completes once enough good responses arrive, once all responses arrive with one good response, or fails with `NT_STATUS_NOT_FOUND` if no acceptable server responds.

## State and Persistence Behavior

State is per-tevent request and talloc-owned. No durable cache is written here; callers decide whether to store site or negative-connection information. Network state includes transient TCP, TLS, tldap, and CLDAP sockets.

## Dependencies and Integration Points

It depends on tevent, tsocket, tstream, tldap, CLDAP, TLS helpers, LDAP NDR encoders, NetLogon response parsers, loadparm client netlogon ping protocol selection, and Samba NTSTATUS utilities. `ldap.c` calls `netlogon_pings` from DC discovery.

## Risks and Test Signals

Risks include the `timeout` argument being stored but not visibly applied to individual ping sends, StartTLS/LDAPS discovery using `TLS_VERIFY_PEER_NO_CHECK`, filter values not being escaped as regular LDAP strings because they are mostly NDR-encoded or caller-provided names, off-by-one assumptions around `wanted_servers <= num_servers`, and accepting one good answer even when more were requested after all replies. Tests should cover every protocol enum, invalid proto, filter construction, required flag combinations, paused responses, malformed netlogon blobs, no-result searches, staggered send ordering, wanted-server thresholds, and timeout/cancellation behavior.
