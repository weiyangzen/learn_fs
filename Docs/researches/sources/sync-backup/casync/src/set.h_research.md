# sources/sync-backup/casync/src/set.h

Purpose: exposes a key-only set API implemented on top of the hashmap backend.

Important APIs/types/functions: `set_new`, free/free_free/copy, ensure-allocated, `set_put`, `set_get`, contains/remove, remove-and-put, merge, reserve, move/move_one, size/isempty/buckets, iteration, clear, first/steal-first, `SET_FOREACH`, and cleanup macros.

Control flow/state: all operations are thin wrappers around hashmap internals where the key is both identity and stored payload. `NULL` sets behave as empty for read paths through the hashmap base convention.

Dependencies/integration: includes `hashmap.h` and `util.h`; uses hash ops supplied by callers. Match trees, collections, and cache bookkeeping can use it for de-duplication.

Risks/test signals: ownership helpers such as `set_free_free` free stored keys, so callers must not mix borrowed and owned keys. Iteration ordering is undefined. Coverage is indirect through code that uses sets to deduplicate IDs or strings.

Source research group: `subset-b-009122`.
