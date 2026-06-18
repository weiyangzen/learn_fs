# sources/user-network-fs/mergerfs/vendored/libfuse/lib/node.cpp

## Purpose
`node.cpp` provides pooled allocation and cleanup for `node_t` objects used by the high-level FUSE namespace cache.

## Important APIs, Types, and Functions
Exports are `node_alloc`, `node_free`, `node_gc`, and `node_clear`, backed by a static `ObjPool<node_t> g_NODE_POOL`.

## Control Flow
`fuse.cpp` requests nodes for root, lookup, create/tmpfile provisional ids, and path entries. Freed nodes return to the pool. Maintenance GC calls `node_gc` for basic cleanup and `node_clear` for thorough cleanup.

## State and Persistence
The object pool is global and process-local. It caches memory for reuse but no node identity persists once freed or across process restarts.

## Dependencies and Integration Points
The file depends on `node.hpp` and `objpool.hpp`. It is one of the key memory-management dependencies of `fuse.cpp`.

## Risks
Pool reuse means `node_t` fields must be fully initialized by callers before use. Clearing the pool while live nodes exist would be unsafe unless `ObjPool` protects against it or only free objects are cleared.

## Test Signals
Use lookup/forget churn, GC under load, sanitizer runs for use-after-free, and assertions around `node_t` initialization after reuse.
