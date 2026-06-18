# sources/user-network-fs/samba/source3/libads/ldap_schema_oids.h

## Purpose

`ldap_schema_oids.h` centralizes string constants for AD/SFU/RFC2307 LDAP attribute OIDs used to discover POSIX attribute display names dynamically.

## Important APIs, Types, and Functions

The file defines six OIDs each for Services for Unix 3.x, Services for Unix 2.0, and RFC2307: uidNumber, gidNumber, homeDirectory, loginShell, gecos, and uid.

## Control Flow

There is no executable flow. `ldap_schema.c` selects one OID set based on `enum wb_posix_mapping` and searches the schema for matching `attributeId` objects.

## State and Persistence Behavior

No state is kept. The constants are compile-time schema identifiers.

## Dependencies and Integration Points

The header has only include guards and macro definitions. It integrates with POSIX schema detection and indirectly with winbind NSS/idmap behavior.

## Risks and Test Signals

Risks are typo-sensitive OID constants and divergence from Microsoft/RFC schema definitions. Tests should verify that every OID constant maps to an expected attribute in representative AD schema fixtures and that adding new schema modes updates both this header and `ldap_schema.c`.
