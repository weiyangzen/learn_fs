# sources/user-network-fs/samba/source3/winbindd/idmap_rfc2307.c

## Purpose
This read-only backend maps SIDs and Unix IDs through RFC2307 user/group records. It performs two-stage mapping: SID/name resolution through winbind/AD, then name/UID/GID lookup in either AD LDAP or a stand-alone LDAP server.

## Important APIs, Types, And Functions
`struct idmap_rfc2307_context` stores bind paths, LDAP domain override, `user_cn`, realm, active LDAP pointer, connection check/search function pointers, ADS state, and stand-alone smbldap state. Initialization is split between `idmap_rfc2307_init_ads`, `idmap_rfc2307_init_ldap`, and `idmap_rfc2307_initialize`. Mapping functions are `idmap_rfc2307_unixids_to_sids` and `idmap_rfc2307_sids_to_unixids`, with helpers for ADS/LDAP search and result matching.

## Control Flow
Initialization requires `bind_path_user`, `bind_path_group`, and `ldap_server` set to `ad` or `stand-alone`. AD mode configures cached ADS connection checks and searches; stand-alone mode reads `ldap_url` and optional `ldap_user_dn` secret, then initializes smbldap. Unix-ID-to-SID builds batched user and group RFC2307 filters, searches LDAP, extracts names and numeric IDs, then calls `winbind_lookup_name` to obtain SIDs. SID-to-Unix-ID first calls `winbind_lookup_sid` to determine names and SID types, uppercases names into an internal map array, searches RFC2307 records by `uid`/`cn`, and assigns IDs.

## State And Persistence
The backend stores only connection/config state. RFC2307 records and AD directory content are authoritative; no allocations or local durable mappings are created. The destructor frees ADS and smbldap state.

## Dependencies And Integration
It depends on `smbldap`, ADS helpers, winbind client lookup utilities, idmap config, global event context, and SID helpers. It temporarily enables winbind recursion around lookup calls with `winbind_on/off`.

## Risks And Test Signals
Test both `ldap_server` modes, missing bind paths, missing LDAP URL, authenticated/anonymous stand-alone LDAP, `ldap_domain` override, `realm` suffixing/stripping, `user_cn`, mixed UID/GID batches, and name case behavior. The code uppercases names and builds LDAP filters without visible escaping, so special characters in names and realms deserve explicit tests. Result arrays are status-based; tests should verify unmapped entries remain clear when LDAP returns unrelated records.
