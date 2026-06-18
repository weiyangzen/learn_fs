# sources/user-network-fs/samba/source3/winbindd/idmap_ad_nss.c

## Purpose

`sources/user-network-fs/samba/source3/winbindd/idmap_ad_nss.c` implements NSS-info plugins that map between AD account names and POSIX aliases using SFU, SFU20, or RFC2307 schema attributes. The source was read as a complete 416-line file.

## Important APIs, Types, and Functions

Important functions are `idmap_ad_nss_init`, `nss_ad_generic_init`, `nss_sfu_init`, `nss_sfu20_init`, `nss_rfc2307_init`, `nss_ad_map_to_alias`, `nss_ad_map_from_alias`, `ad_idmap_cached_connection`, and `ad_map_type_string`. It defines a local `struct idmap_ad_context` with ADS connection, `posix_schema`, and map type.

## Control Flow

Plugin initialization registers three `nss_info_methods` tables under names `rfc2307`, `sfu`, and `sfu20`. Each init function creates or reuses an `idmap_domain` in the NSS domain entry and sets the desired POSIX mapping type. Alias mapping obtains a cached ADS connection, loads schema details if needed, searches by `sAMAccountName` to read the POSIX uid alias, or searches by POSIX uid alias to return `WORKGROUP\samAccountName`.

## State and Persistence Behavior

The plugin caches ADS connection/schema state in the NSS domain entry. It reads LDAP/AD attributes only and does not persist mappings. It refuses online lookups when winbind is in offline-logon state.

## Dependencies and Integration Points

It depends on ADS cached connections, `ads_check_posix_schema_mapping`, ADS LDAP search helpers, Samba idmap offline state, `nss_info` plugin registration, loadparm workgroup, and AD schema definitions from `libads/ldap_schema.h`.

## Risks and Edge Cases

The parameter validation in `nss_ad_map_to_alias` checks `!*alias`, which assumes the caller passes a non-null pointer with current content semantics; this is easy to misuse. LDAP filters interpolate names/aliases and need correct escaping behavior from callers or ADS helpers. Offline mode returns `NT_STATUS_FILE_IS_OFFLINE`. Schema absence returns object path/name errors.

## Test Signals

Tests should cover all three plugin registrations, map-type override warnings, offline behavior, missing schema, successful name-to-alias and alias-to-name LDAP searches, no-result handling, and invalid parameter cases.
