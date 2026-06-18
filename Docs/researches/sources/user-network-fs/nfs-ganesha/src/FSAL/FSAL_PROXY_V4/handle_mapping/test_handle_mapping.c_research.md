# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/test_handle_mapping.c

## Purpose
Standalone test/benchmark for the full handle mapping API: init, set, get, delete, and flush.

## Important APIs, Types, and Functions
Uses `HandleMap_Init`, `HandleMap_SetFH`, `HandleMap_GetFH`, `HandleMap_DelFH`, `HandleMap_Flush`, `handle_map_param_t`, and `nfs23_map_handle_t`.

## Control Flow
Validates `<db_dir> <db_count>`, initializes logging and mapping, inserts 10,000 synthetic mappings, times insertion, retrieves and deletes them, flushes DB work, logs total timing, and exits on unexpected errors.

## State and Persistence Behavior
Mutates a caller-provided SQLite handle-map directory and uses `/tmp` for temp work. Generated hashes include `time(NULL)`, so interrupted runs can leave variable stale rows.

## Dependencies and Integration Points
Built by local CMake and links against handle mapping, hashtable/log/common utilities, rwlock, and SQLite.

## Risks
The source appears stale: it assigns removed config fields and calls mapping functions with older argument counts. It should use a scratch DB directory, not production mapping storage.

## Test Signals
Successful compilation, 10,000 set/get/delete operations, flush completion, and expected empty/deleted DB rows afterward.
