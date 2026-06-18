# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_db.h

## Purpose
Declares the internal SQLite database layer for PROXY_V4 handle mapping and defines database/table/column naming constants.

## Important APIs, Types, and Functions
Constants: `DB_FILE_PREFIX`, `MAP_TABLE`, `OBJID_FIELD`, `HASH_FIELD`, `HANDLE_FIELD`, and `MAX_DB`. Functions: count, init, reload all, insert, delete, and flush.

## Control Flow
Normal use is count existing shards, initialize workers/connections, reload rows into a hashtable, enqueue runtime mutations, and flush for synchronization.

## State and Persistence Behavior
The header defines naming and shard limits but owns no state. `MAX_DB` caps worker/database instances at 32.

## Dependencies and Integration Points
Includes `handle_mapping.h` and `hashtable.h`. Used by mapping implementation and test programs.

## Risks
The misspelled `handlemap_db_reaload_all` is part of the local ABI. Reload requires a valid target hashtable in normal operation. Header changes require synchronized implementation and test updates.

## Test Signals
Compilation plus creation of `handlemap.sqlite.<n>` files with the expected `HandleMap` schema.
