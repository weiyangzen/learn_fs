# sources/user-network-fs/samba/source4/libcli/finddcs_cldap.c

Purpose: implements domain controller discovery through DNS/NBT name resolution followed by CLDAP Netlogon pings.

Important APIs: `finddcs_cldap_send()`, `finddcs_cldap_recv()`, and synchronous `finddcs_cldap()`. Internal stages include IP bypass, DNS SRV lookup, NBT `<1C>` lookup, explicit hostname lookup, `finddcs_cldap_next_server()`, and `finddcs_cldap_netlogon_replied()`.

Control flow: send copies relevant inputs into request state, chooses the path: explicit IP goes straight to CLDAP, explicit hostname uses NBT server lookup, dotted domain uses DNS SRV `_ldap._tcp[.site]._sites.domain`, and non-dotted domain uses NBT logon lookup. Resolved addresses are converted to `tsocket_address` entries on port 389. `netlogon_pings_send()` queries all candidates with `NETLOGON_NT_VERSION_5`, `5EX`, and `IP`, required flags, optional realm and SID, and a two-second timeout. The receive callback chooses a non-null response, maps it, and completes.

State and persistence: `finddcs_cldap_state` is talloc-owned by the `tevent_req`; no disk persistence. The selected response and address are moved/steolen to caller memory on recv.

Dependencies and integration: mixes modern `tevent_req` with older composite resolver callbacks. Depends on CLDAP, resolver, Netlogon ping helpers from source3, tsocket, SID utilities, and composite helpers.

Risks: `finddcs_cldap_ipaddress()` returns `tevent_req_is_nterror()` in a way that means successful immediate submission can return false; tests should confirm this path. Hostname resolution uses NBT server name rather than DNS unless the server address is already numeric. The final non-null response wins in the loop. Test signals include explicit IP, DNS SRV with and without site, NBT fallback, no-response handling, minimum flag filtering, domain SID filtering, timeout behavior, and sync `finddcs_cldap_recv()` polling.
