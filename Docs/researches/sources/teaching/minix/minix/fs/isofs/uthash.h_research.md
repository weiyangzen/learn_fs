# File Research: sources/teaching/minix/minix/fs/isofs/uthash.h

This is a complete embedded copy of Troy D. Hanson's `uthash` single-header hash table library, version `1.9.9`, used by ISOFS code as a macro-based intrusive hash table implementation. It is not MINIX-specific logic, but it provides reusable hash table primitives that callers embed by placing a `UT_hash_handle` field in their own structures.

The header defines compiler portability helpers (`DECLTYPE`, `DECLTYPE_ASSIGN`, Windows integer type fallbacks), allocator/error override hooks (`uthash_malloc`, `uthash_free`, `uthash_fatal`), optional bloom-filter support, and the public CRUD-style macros: `HASH_FIND`, `HASH_ADD`, `HASH_REPLACE`, `HASH_DELETE`, `HASH_CLEAR`, `HASH_ITER`, `HASH_COUNT`, and convenience variants for string, integer, and pointer keys. Items are tracked in both bucket chains and an application-order doubly linked list.

Hashing defaults to Jenkins (`HASH_JEN`) but includes Bernstein, SAX, FNV-1a, one-at-a-time, Hsieh/SFH, and optional MurmurHash variants. Bucket arrays start at 32 buckets and double when bucket chains exceed the threshold, with expansion suppression if repeated expansion does not improve distribution.

Important structs are `UT_hash_bucket`, `UT_hash_table`, and `UT_hash_handle`. The implementation is macro-only and relies on caller-owned storage for elements and keys; deletion frees only table metadata when the final item is removed, not user elements.
