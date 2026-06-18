# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/test_handle_mapping_db.c

## Purpose
Standalone test/benchmark for the lower-level SQLite DB queue API behind handle mapping.

## Important APIs, Types, and Functions
Uses `handlemap_db_count`, `handlemap_db_init`, `handlemap_db_reaload_all`, `handlemap_db_insert`, `handlemap_db_delete`, `handlemap_db_flush`, and synthetic `nfs23_map_handle_t` keys.

## Control Flow
Parses DB dir/count, counts shards, initializes DB workers, reloads all rows, submits 10,000 inserts and flushes, submits 10,000 deletes and flushes, logging elapsed times.

## State and Persistence Behavior
Creates and mutates `handlemap.sqlite.<n>` files in the supplied directory. Queue mutations are async until flush.

## Dependencies and Integration Points
Depends on the DB implementation, SQLite, pthreads, and Ganesha logging. Built by the local CMake file.

## Risks
The `handlemap_db_init` call does not match the current header signature, and `handlemap_db_reaload_all(NULL)` is unsafe if rows exist. The test should only run against scratch DB directories.

## Test Signals
DB shard count, insert/delete timing logs, flush logs, and absence of SQLite errors or queue stalls.
