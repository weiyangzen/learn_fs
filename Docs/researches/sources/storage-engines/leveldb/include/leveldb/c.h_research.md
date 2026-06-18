# sources/storage-engines/leveldb/include/leveldb/c.h

Purpose: declares LevelDB's C ABI wrapper, intended for stable shared-library use and bindings such as JNI.

Important APIs and types: opaque handles for DB, options, read/write options, iterators, snapshots, batches, cache, comparator, filter policy, env, logger, and file abstractions; functions for open/close, put/delete/write/get, iterator movement/access, snapshots, properties, approximate sizes, compaction, destroy/repair, write-batch operations, option setters, comparator/filter construction, cache/env creation, memory free, and version reporting.

Control flow: callers allocate option/handle objects, pass raw pointer-plus-length slices instead of C++ `Slice`, receive heap-allocated results/errors, and destroy/free objects with matching C API functions.

State and persistence behavior: maps directly onto the C++ DB and WAL/table/MANIFEST behavior. Error strings and returned values are malloc-owned by the library and must be released with `leveldb_free`.

Dependencies and integration: uses `LEVELDB_EXPORT` and `extern "C"` to expose ABI symbols. The implementation lives elsewhere but wraps public C++ APIs.

Risks and edge cases: custom C comparators do not expose key-shortening hooks, and the API cannot implement custom DB/env/cache/iterator types. All pointer arguments must be non-null. Error-pointer ownership rules are strict, especially on Windows allocators.

Test signals: C API coverage is not in this subset; behavior is indirectly tied to public DB tests.
