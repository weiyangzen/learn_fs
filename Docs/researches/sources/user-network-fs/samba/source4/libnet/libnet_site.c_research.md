# sources/user-network-fs/samba/source4/libnet/libnet_site.c

## Purpose

`libnet_site.c` supports domain-join site placement. It discovers the client's AD site using CLDAP netlogon pings, constructs configuration/server DNs, and creates or updates the `server` object under `CN=Sites,CN=Configuration,...` for the joining machine.

## Important APIs, Types, and Functions

`libnet_FindSite()` takes a destination DC address, local NetBIOS name, and domain DN. It sends a CLDAP/netlogon ping to port 389, defaults to `Default-First-Site-Name`, replaces it with `client_site` from a NETLOGON NT5EX response when present, and returns `site_name_str`, `config_dn_str`, and `server_dn_str`.

`libnet_JoinSite()` resolves the SAMR binding host to an address, calls `libnet_FindSite()`, builds an LDB `server` object with `objectClass=server`, `systemFlags=50000000`, and `serverReference=<machine account DN>`, then `ldb_add()`s it or replaces `serverReference` if it already exists.

## Control Flow

Join-site flow derives the host from `libnet_JoinDomain` output SAMR binding, resolves it as an NBT client name, discovers site/DNs, constructs an LDB message, validates the target DN, adds the server object, and on existing entry performs a replace-only modify of `serverReference`. On success it stores `server_dn_str` into the broader join result.

## State and Persistence Behavior

`FindSite` only returns derived strings. `JoinSite` mutates the remote AD configuration partition by adding or modifying a server object. It does not create `CN=NTDS Settings`; a debug message explicitly notes that a future `DsAddEntry()` is still needed. Temporary allocations are freed through `tmp_ctx`; successful server DN is stolen into the join result.

## Dependencies and Integration Points

Dependencies include CLDAP/netlogon ping helpers, resolve APIs, tsocket address construction, LDB add/modify, Samba loadparm for netlogon ping protocol and resolver context, and join-result structures from `libnet_JoinDomain`. It sits in the domain-join flow with machine account creation and SAMR binding discovery.

## Risks and Edge Cases

The configuration DN is generated as `CN=Configuration,<domain DN>` rather than discovered. CLDAP failure does not abort site selection; it silently uses the default site. `resolve_name_ex()` and LDB errors are surfaced inconsistently, with some paths setting `error_string` to NULL. Existing server entries only update `serverReference`, which may leave stale attributes. Missing NTDS Settings creation means this file alone is not a complete DC site-registration implementation.

## Test Signals

Integration tests should verify CLDAP site discovery, default-site fallback, correct DN construction, add-vs-modify behavior on existing server objects, invalid DN handling, and join flows that later consume `server_dn_str`.
