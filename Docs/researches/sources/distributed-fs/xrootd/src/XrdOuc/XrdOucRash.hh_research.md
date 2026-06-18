# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucRash.hh

Purpose: declares a templated radix-tree cache/table, `XrdOucRash<K,V>`, for binary integral keys and values. It provides hash-like add, replace, lookup, delete, purge, and scan behavior while indexing by nibbles of the key rather than computing a conventional hash.

Important APIs, types, and functions: `XrdOucRash_Options` controls replacement and duplicate-count semantics. `XrdOucRash_Item` stores key, value, expiration time, and duplicate count. `XrdOucRash_Tent` owns either a child table or one item. Public table methods are `Add()`, `Rep()`, `Del()`, `Find()`, `Apply()`, `Purge()`, and `Num()`. The implementation is included from `XrdOucRash.icc`.

Control flow: `Add()` looks up an existing key, optionally increments a count, returns existing unexpired data unless replacement is requested, or inserts a newly allocated item. `Find()` lazily expires stale entries. `Del()` decrements counted entries before removing them. `Apply()` recursively visits all 16-way child tables and lets a callback delete, continue, or stop at an item.

State and persistence: state is a root array of 16 entries, dynamically allocated child arrays, item objects, and `rashnum`. Expiration is wall-clock based through `time(0)`. There is no persistence and no internal locking; the header explicitly requires external serialization for multi-threaded use.

Dependencies and integration points: depends on `<ctime>`, `<sys/types.h>`, errno values from the included implementation, and `XrdSysPlatform.hh` endian definitions for key conversion. It is useful for small in-memory caches keyed by fixed-width binary identifiers.

Risks and test signals: replacement of an expired existing item calls `Set()` with `KeyTime` still zero in the implementation, so lifetime refresh on expired replacement should be checked. The structure is not MT-safe, recursive deletion depends on ownership in `XrdOucRash_Tent`, and key type assumptions are limited to integral-like objects fitting into 64 bits. Tests should cover add/find/replace, expiration, `Rash_count`, deletion during `Apply()`, endian behavior, and purge cleanup.
