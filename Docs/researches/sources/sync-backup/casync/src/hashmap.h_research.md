# sources/sync-backup/casync/src/hashmap.h

Purpose: declares casync's imported systemd-style generic hash container API: plain `Hashmap`, insertion-ordered `OrderedHashmap`, and key-only `Set`, all backed by the opaque `HashmapBase` implementation in `hashmap.c`. It lets callers treat `NULL` maps as empty for reads, which reduces allocation noise across optional metadata paths.

Important APIs/types/functions: exposes `Iterator`, `ITERATOR_FIRST`, allocation/free/copy helpers, put/update/replace/get/get2/contains/remove variants, merge/move/reserve, size/bucket inspection, first/steal-first helpers, ordered next lookup, `*_get_strv`, and `HASHMAP_FOREACH*` macros. GCC type-checking macros (`HASHMAP_BASE`, `PLAIN_HASHMAP`) intentionally reject incompatible pointer families at compile time.

Control flow/state: the header is mostly inline wrappers around internal polymorphic functions. Iteration state is caller-owned in `Iterator`; debug builds add mutation counters and source location plumbing via `HASHMAP_DEBUG_*`.

Dependencies/integration: depends on `hash-funcs.h` for hash/equality operations and `util.h` for cleanup macros. `set.h` builds its public API directly on these calls.

Risks/test signals: misuse risk is iterator invalidation, freeing ownership confusion in `free_free` helpers, and mixing map types outside permitted merge cases. Coverage is indirect through match/origin/name-table code using maps/sets rather than a dedicated hashmap test here.

Source research group: `subset-b-009122`.
