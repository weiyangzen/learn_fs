# sources/storage-engines/rocksdb/memory/concurrent_arena.cc

Purpose: Implementation details for `ConcurrentArena` construction and shard selection.

Important APIs/types/functions: thread-local `tls_cpuid`, constructor, `Repick`, constant `kMaxShardBlockSize`.

Control flow and state: constructor chooses shard block size as `min(128KB, block_size / 8)`, initializes the underlying `Arena`, and snapshots accounting via `Fixup`. `Repick` obtains a core-local shard and index, stores a nonzero encoded shard id in TLS, and returns the shard.

State and persistence behavior: in-memory thread-local shard selection and arena memory only.

Dependencies and integration points: `CoreLocalArray`, `Random` include, port threading support, `Arena`.

Risks: shard sizing trades contention reduction against fragmentation; very small block sizes can reduce shard utility. TLS cpu id can become stale after thread migration but design tolerates approximate sharding.

Test signals: no dedicated test in this subset; exercised indirectly by memtable/concurrent allocation users.
