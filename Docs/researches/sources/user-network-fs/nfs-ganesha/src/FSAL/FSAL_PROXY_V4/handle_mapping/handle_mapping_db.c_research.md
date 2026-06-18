# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping_db.c

## Purpose
Provides SQLite persistence for the PROXY_V4 handle map. It shards rows across database files, starts one worker per shard, reloads rows into the in-memory map, and asynchronously handles insert/delete requests.

## Important APIs, Types, and Functions
Public API: `handlemap_db_count`, `handlemap_db_init`, `handlemap_db_reaload_all`, `handlemap_db_insert`, `handlemap_db_delete`, and `handlemap_db_flush`. Internal types include `db_op_item_t`, `flusher_queue_t`, and `db_thread_info_t`; operation types are `LOAD`, `INSERT`, and `DELETE`.

## Control Flow
Initialization records directories, sets SQLite temp directory, initializes queues/pools, and starts worker threads. Workers open `handlemap.sqlite.<index>`, create schema, prepare SQL statements, then drain high-priority load/insert tasks before lower-priority deletes. Flush waits until all queues are idle.

## State and Persistence Behavior
Rows persist in table `HandleMap(ObjectId, HandleHash, FSALHandle)`. Handles are stored as uppercase hex strings. Queue state is in memory and protected by mutexes/conditions. Inserts are async when `synchronous` is false; deletes are always async.

## Dependencies and Integration Points
Depends on SQLite3, pthreads, directory scanning, Ganesha pools/logging, and `handle_mapping_hash_add`. Called only through the public mapping layer and tests.

## Risks
The synchronous insert mode is not implemented. Worker operation failures are logged but not propagated after dequeue. There is no visible shutdown/join path. Passing `NULL` to reload, as the DB test does, is unsafe if rows exist.

## Test Signals
DB count, worker initialization, reload logs, 10,000 insert/delete benchmark loops, flush completion, and expected SQLite rows/files.
