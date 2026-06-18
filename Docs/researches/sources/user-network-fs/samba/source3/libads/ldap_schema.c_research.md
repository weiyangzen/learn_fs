# sources/user-network-fs/samba/source3/libads/ldap_schema.c

## Purpose

`ldap_schema.c` resolves AD schema metadata needed by Samba, especially POSIX attribute names for SFU, SFU 2.0, and RFC2307 mappings, plus lookup helpers for schema GUIDs and schema naming context.

## Important APIs, Types, and Functions

`ads_schema_path` reads `schemaNamingContext` from RootDSE. `ads_get_attrname_by_guid` encodes a schema GUID as LDAP NDR and searches `schemaIDGUID`. `ads_check_posix_schema_mapping` fills a `struct posix_schema` for a selected `enum wb_posix_mapping`. The internal `ads_get_attrnames_by_oids` searches for `attributeId` values and returns matching `lDAPDisplayName` names with OID/name arrays.

## Control Flow

For POSIX schema mapping, template/unixinfo modes return success without LDAP schema lookups. SFU, SFU20, and RFC2307 modes choose the corresponding OID arrays from `ldap_schema_oids.h`, fetch the schema DN, search for all requested OIDs under the schema container, and map each returned OID to the correct `posix_schema` field. The helper reports `STATUS_SOME_UNMAPPED` if fewer schema objects are returned than requested.

## State and Persistence Behavior

No global state is kept. Returned schema names are allocated under the caller-provided memory context through a `struct posix_schema`; temporary OID/name arrays live under an internal talloc context. The source of truth is AD schema state.

## Dependencies and Integration Points

It depends on ADS search/retry helpers, schema OID constants, LDAP NDR GUID encoding, and `ldap_schema.h` declarations. It integrates with winbind NSS/idmap code that must know the actual AD display names for Unix attributes instead of assuming one schema flavor.

## Risks and Test Signals

Risks include schema searches returning unordered results, missing optional `posix_uid_attr` not being validated while other fields are required, OID arrays not being NULL-terminated even though the helper checks only `num_OIDs`, and treating allocation failures and missing required mappings similarly. Tests should mock or exercise SFU/SFU20/RFC2307 schemas, partial OID matches, unknown map type, RootDSE schema DN failures, GUID lookup with zero/multiple hits, and memory ownership of returned schema strings.
