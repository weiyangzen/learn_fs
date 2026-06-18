# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_internal.h

## Purpose
Shares narrow internal helpers between the in-memory and SQLite handle-mapping implementation files.

## Important APIs, Types, and Functions
Declares `handle_mapping_hash_add` for inserting a decoded mapping and `sscanmem` for hex-to-binary conversion.

## Control Flow
Database reload decodes each SQLite handle string with `sscanmem`, then calls `handle_mapping_hash_add` to repopulate the live map.

## State and Persistence Behavior
No state. Declared functions mutate mapping hash state and decode persistent row contents.

## Dependencies and Integration Points
Depends on `hashtable.h`; included by `handle_mapping.c` and `handle_mapping_db.c`.

## Risks
The hash-add signature accepts a target hash, but implementation currently uses global state. Changes to pooled key/value layout must preserve reload expectations.

## Test Signals
Successful reload of non-empty DBs and retrievable mappings through `HandleMap_GetFH`; malformed hex rows exercise `sscanmem` failures.
