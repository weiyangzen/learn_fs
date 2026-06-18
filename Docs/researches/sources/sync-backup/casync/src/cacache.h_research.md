# sources/sync-backup/casync/src/cacache.h

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cacache.h -->
## sources/sync-backup/casync/src/cacache.h

Purpose: `cacache.h` declares the opaque `CaCache` API used to memoize source location to chunk/origin mappings.

Important APIs and types: `typedef struct CaCache CaCache` hides implementation details. Public functions create, ref, unref, set digest type, configure by fd or path, get a mapping, put a mapping, and remove a mapping. `DEFINE_TRIVIAL_CLEANUP_FUNC(CaCache*, ca_cache_unref)` provides cleanup-attribute integration.

Control flow contract: callers allocate a cache, configure either fd or path before use, optionally set a digest type before any digest is created, then call get/put/remove. `ca_cache_get` can return a chunk ID and optionally transfer a referenced `CaOrigin`.

State and persistence: the header abstracts persistent cache entries stored by `cacache.c`. The API implies reference counting and ownership transfer for returned origins.

Dependencies and integration points: includes `cachunkid.h`, `calocation.h`, `caorigin.h`, and `util.h`, so users get chunk IDs, location objects, origin objects, and cleanup macros. It is consumed by chunk generation/matching code.

Risks: the fd/path setters are mutually exclusive and are one-shot in the implementation. Changing digest type after cache use returns busy. Callers must respect negative errno-style returns.

Test signals: compile-level tests should ensure the opaque type remains hidden and cleanup macro works. Behavioral tests belong with `cacache.c`.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cacache.h -->
