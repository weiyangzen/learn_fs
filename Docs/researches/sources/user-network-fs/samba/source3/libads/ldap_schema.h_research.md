# sources/user-network-fs/samba/source3/libads/ldap_schema.h

## Purpose

`ldap_schema.h` declares Samba's ADS schema lookup surface for POSIX attribute mapping and schema GUID resolution.

## Important APIs, Types, and Functions

`struct posix_schema` stores AD display names for POSIX home directory, shell, uidNumber, gidNumber, gecos, and uid attributes. `enum wb_posix_mapping` names supported mapping modes: unknown, template, SFU, SFU20, RFC2307, and unixinfo. Function declarations expose `ads_get_attrname_by_guid`, `ads_schema_path`, and `ads_check_posix_schema_mapping`.

## Control Flow

The header has no runtime flow. Callers choose a mapping enum, call `ads_check_posix_schema_mapping`, and then use the returned attribute names in subsequent LDAP searches. GUID consumers call `ads_get_attrname_by_guid` after obtaining the schema DN.

## State and Persistence Behavior

The header defines only caller-owned data contracts. `struct posix_schema` instances are talloc-allocated by the implementation and reflect current AD schema metadata.

## Dependencies and Integration Points

It depends on ADS types, `TALLOC_CTX`, `ADS_STATUS`, and `struct GUID` declarations provided by broader Samba includes. It integrates with `ldap_schema.c`, winbind POSIX mapping, idmap backends, and ACL/security display code that resolves schema GUIDs to readable names.

## Risks and Test Signals

Risks are ABI drift if fields or enum values are changed without updating users, lack of explicit ownership comments for returned `struct posix_schema`, and compile-time dependency on `ADS_STRUCT` being declared before inclusion. Tests should include compile coverage for all consumers and runtime schema mapping for every enum branch.
