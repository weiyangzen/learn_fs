# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PROXY_V4/handle_mapping/handle_mapping.c

## Purpose
Implements the in-memory front end for PROXY_V4's persistent mapping from compact NFSv3-compatible digests to full proxy handle blobs containing remote NFSv4 filehandles.

## Important APIs, Types, and Functions
Public API: `HandleMap_Init`, `HandleMap_GetFH`, `HandleMap_SetFH`, `HandleMap_DelFH`, and `HandleMap_Flush`. Shared helper: `handle_mapping_hash_add`. Private pool entry types hold digest keys and stored handle blobs.

## Control Flow
Initialization validates existing DB shard count, initializes DB workers, creates pools and hashtable, then reloads persisted rows. Set inserts into the hashtable without overwrite and queues a DB insert. Get latches and copies a stored handle. Delete removes from hash, frees pooled storage, and queues a DB delete. Flush drains DB queues.

## State and Persistence Behavior
Owns global `handle_map_hash`, `digest_pool`, and `handle_pool`. Mappings become immediately visible in memory and are asynchronously persisted by `handle_mapping_db.c`. Reload restores prior rows at startup.

## Dependencies and Integration Points
Depends on Ganesha hashtable/pool/logging APIs, `handle_mapping_db`, and NFSv4 handle sizing. Used by `handle.c` for NFSv3 handle digest expansion and storage.

## Risks
Global state is not per export. `handle_mapping_hash_add` takes a hash parameter but inserts into the global hash. Async persistence can lose recently issued mappings on crash unless flushed. Digest uniqueness relies on object id plus non-cryptographic handle hash.

## Test Signals
`test_handle_mapping.c` should initialize, set/get/delete 10,000 mappings, and flush. Reload count and stale lookup behavior are useful negative/positive signals.
