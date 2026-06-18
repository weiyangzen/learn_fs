# sources/storage-engines/rocksdb/db/wide/read_path_blob_resolver.h

Purpose: Declares `ReadPathBlobResolver`, the public internal class for read-path lazy blob resolution of wide-column entities. The header defines the ownership/lifetime contract and the resolver operations used by DBIter and point lookup code.

Important APIs/types/functions: The constructor accepts `Version*`, `ReadTier`, checksum and cache flags, `Env::IOActivity`, optional `BlobFileCache`, and `allow_write_path_fallback`. `Reset` binds the resolver to a user key plus parsed `std::vector<WideColumn>` and blob-column metadata. `ResolveColumn`, `ResolveColumns`, and `ResolveAllColumns` fetch or expose column values. `IsUnresolvedColumn`, `HasUnresolvedColumns`, and `NumColumns` query resolver state. `RegisterCleanup` forwards cleanup registration to the embedded `Cleanable`.

Control flow contract: Callers reset the resolver for each entity after V2 deserialization, then either resolve selected columns lazily or force all blob columns to be fetched. Inline columns are returned without IO; blob columns may fetch from blob files and cache the result. The header makes clear that `ResolveColumn` can fail for out-of-bounds indexes or blob IO errors.

State and persistence behavior: The class owns a `BlobFetcher`, current key slice, non-owning pointers to columns and blob metadata, a vector cache of resolved blob values, and a `Cleanable` for lifetime pinning. It persists no state itself, but it depends on blob files remaining available and on caller-pinned version resources. `Reset` clears the cache so blob values from one entity cannot leak into another.

Dependencies: The header includes blob fetch/index types, RocksDB `Cleanable`, `Options`/`ReadTier`, `Slice`, `Status`, and `wide_columns.h`. It forward-declares `Version` and exposes `BlobFileCache` through the constructor.

Integration points: The documented users are iterator (`DBIter`) and point-lookup (`GetEntity` via `PinnableWideColumns`) paths. The TODO notes duplication with `CompactionBlobResolver`, indicating a shared logical contract across read and compaction paths but different blob-fetching backends and stats contexts.

Risks and edge cases: The class is explicitly not thread-safe. `Version*`, `columns`, and `blob_columns` must outlive the resolver or next reset. Because resolved slices can point into internal cache storage, callers must respect resolver lifetime. `RegisterCleanup` is critical for SuperVersion pinning; missing cleanup registration can cause use-after-free of version/blob metadata.

Test signals: Coverage is indirect through read-path tests for blob-backed wide columns, block-cache-tier incomplete handling, read-only reopen, direct-write memtable reads, iterator eager resolution, and multi-get entity behavior.
