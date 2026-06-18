# sources/user-network-fs/samba/source3/registry/reg_db.h

## Purpose
`reg_db.h` centralizes constants for Samba's internal registry database format and dbwrap/tdb flags.

## Important APIs, Types, And Functions
The header defines `REG_TDB_FLAGS` as `TDB_SEQNUM`, `REG_DBWRAP_FLAGS` as `DBWRAP_FLAG_NONE`, database format versions `REGDB_VERSION_V1`, `REGDB_VERSION_V2`, `REGDB_VERSION_V3`, and `REGDB_CODE_VERSION` as version 3. It also defines storage key prefixes: `REG_VALUE_PREFIX`, `REG_SECDESC_PREFIX`, and historical `REG_SORTED_SUBKEYS_PREFIX`.

## Control Flow
There is no executable control flow. The constants are consumed by the registry database backend when opening, migrating, and encoding entries in the persistent registry database.

## State And Persistence
This file directly describes persistent format state. `REGDB_CODE_VERSION` is the current database schema level, and the prefix strings shape how values and security descriptors are stored. Version comments indicate that V2 introduced normalized keys and V3 changed key-existence semantics while removing the sorted-subkeys cache.

## Dependencies And Integration Points
The constants are used by `reg_backend_db.c` and related registry database code. `TDB_SEQNUM` is important for sequence-number based cache freshness in higher layers.

## Risks And Test Signals
Changing these constants affects on-disk compatibility. Tests should cover database initialization, migration from older versions, sequence-number behavior, and lookup of values/security descriptors by prefix. Since V3 changed existence semantics, regression tests should include empty keys, keys with only values, and deleted subkey cases.
