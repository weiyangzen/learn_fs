# sources/user-network-fs/samba/source3/winbindd/idmap_ad.c

## Purpose

`sources/user-network-fs/samba/source3/winbindd/idmap_ad.c` implements the `idmap_ad` backend, mapping between Active Directory SIDs and Unix UID/GID values stored in RFC2307/SFU schema attributes. It also optionally enriches winbind user info with Unix primary group and NSS fields from AD. The source was read as a complete 1308-line file.

## Important APIs, Types, and Functions

Key types are `struct idmap_ad_context` and `struct idmap_ad_schema_names`. Important functions include `idmap_ad_init`, `idmap_ad_initialize`, `idmap_ad_get_context`, `idmap_ad_context_create`, `idmap_ad_get_tldap_ctx`, `get_posix_schema_names`, `get_attrnames_by_oids`, `idmap_ad_dn_filter`, `idmap_ad_query_user_retry`, `idmap_ad_unixids_to_sids_retry`, and `idmap_ad_sids_to_unixids_retry`.

## Control Flow

Initialization registers `ad_methods` and the AD NSS plugins. Context creation resolves a DC from gencache, creates private krb5 config, opens LDAP or LDAPS/StartTLS according to `client ldap sasl wrapping`, binds with machine trust credentials, fetches RootDSE, discovers schema attribute names by OID, loads options such as `unix_primary_group`, `unix_nss_info`, `ldap_timeout`, `allow ous`, and `deny ous`, and caches the context in the idmap domain. Mapping functions build LDAP OR filters for requested IDs or SIDs, search under the default naming context, filter returned DNs, infer UID/GID from `sAMAccountType`, and set `id_map` statuses.

## State and Persistence Behavior

The backend keeps a cached LDAP context, schema names, default naming context, OU filters, and options in `dom->private_data`. It reads AD state but does not write AD or local mapping databases. On LDAP server-down/timeout statuses, retry wrappers free cached private data and return `NT_STATUS_HOST_UNREACHABLE` so callers can retry later with a fresh connection.

## Dependencies and Integration Points

It depends on winbind domain/DC discovery, DNS/name resolution, Kerberos private config, trust credentials, tldap, TLS/gensec bind, loadparm, generated netlogon/ADS types, LDAP schema OIDs, LDB DN comparison, global event context, and idmap/NSS plugin registration.

## Risks and Edge Cases

LDAP filter construction must escape encoded SIDs and numeric attributes correctly. AD schema mode must match the directory; missing OID lookups fail context creation. OU allow/deny filters can silently exclude valid objects. The backend refuses use on AD DC builds. Network, TLS, and credential failures are common operational edges. Mapping type inference from `sAMAccountType` must match AD semantics.

## Test Signals

Tests should cover schema-mode OID resolution, LDAP bind/TLS modes, allow/deny OU filtering, UID/GID-to-SID batch mapping, SID-to-UID/GID mapping, timeout/server-down cache reset, `unix_primary_group` and `unix_nss_info` enrichment, AD DC rejection, and registration of both idmap and NSS methods.
