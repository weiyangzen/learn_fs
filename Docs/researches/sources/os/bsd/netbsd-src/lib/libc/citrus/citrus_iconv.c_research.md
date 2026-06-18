# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_iconv.c

Runtime loader and cache for Citrus iconv conversion modules.

Key behavior:
- Initializes a process-wide shared converter cache and unused LRU-like tail queue.
- `ICONV_MAX_REUSE` controls the maximum number of unused shared converters, unless running setugid.
- Resolves source/destination aliases through `iconv.alias`.
- Rejects resolved names containing `/`.
- Looks up `src/dst` in `iconv.dir`, falling back to `*`.
- Loads the converter module, resolves iconv getops, validates ABI v2, and initializes shared converter state.
- `_citrus_iconv_open` creates a per-use context from shared state.
- `_citrus_iconv_close` uninitializes context and returns shared state to the cache or evicts it.

Concurrency:
- Uses a libc rwlock around cache initialization, lookup, reference counts, and eviction.
