# sources/user-network-fs/samba/source3/libads/ads_ldap_protos.h

## Purpose
This header declares LDAP-oriented ADS helper APIs that are implemented across libads LDAP modules. It is a prototype aggregation point for opening LDAP connections, extracting LDAP values, searching, reconnecting, processing results, and parsing AD-specific objects.

## Important APIs and Types
Declared APIs include `ldap_open_with_timeout`, `ads_msgfree`, `ads_get_dn`, pull helpers for strings, ranged strings, uint32, GUID, SID, security descriptors, and usernames, account/printer find helpers, `ads_do_search*` variants, retry/search-by-SID helpers, LDAP message iteration helpers, `ads_process_results`, `ads_dump`, GPO parsing, SD flag searches, token SID lookup, and joinable OU lookup.

## Control Flow and State
As a header, it has no runtime flow. Its API shape shows the central ADS pattern: most functions take `ADS_STRUCT *ads`, return `ADS_STATUS` or extracted talloc-owned values, and operate on `LDAPMessage` results that callers must free with `ads_msgfree`.

## Dependencies and Integration Points
It depends on LDAP types, ADS structures, GUID/SID/security descriptor types, and GPO forward declarations. It is consumed by libads callers that need LDAP operations without including every implementation-specific source header.

## Risks and Test Signals
Risk is prototype drift against implementation files such as `ldap.c`, `ldap_utils.c`, and schema/GPO modules. Compile coverage should include modules using ranged results, retry paths, and security descriptor flag searches.
