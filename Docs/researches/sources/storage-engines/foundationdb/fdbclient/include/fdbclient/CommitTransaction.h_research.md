# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/CommitTransaction.h

Purpose: Defines mutation, transaction, and mutation-version payload types used on the commit path, including compact wire serialization, mutation checksum support, and conflict/mutation collections.

Important APIs/types/functions: `MutationRef` stores a mutation `type`, `param1`, `param2`, optional CRC32C checksum, optional accumulative checksum index, and corruption flag. Mutation types include set/clear, atomic operations, versionstamped mutations, comparison clear, and reserved log/span/partition slots. Helper methods classify atomic/single-key/non-associative operations, copy parameters into arenas, format traces, populate/validate checksums, offload serialized checksum/index suffixes, and serialize with protocol-sensitive checksum flags. `CommitTransactionRef` carries read and write conflict ranges, mutations, read snapshot, conflicting-key reporting, lock awareness, span context, and legacy tenant ids. `MutationsAndVersionRef` bundles mutations with committed and known committed versions.

Control flow: Transaction builders push mutations and conflict ranges into `CommitTransactionRef`. During serialization, `MutationRef` may compact single-key clear ranges by serializing end plus empty begin, and may append checksum then accumulative checksum index to `param2` while setting high bits in `type`. During deserialization, it validates suffix sizes, strips accumulative index before checksum, reconstructs single-key clear ranges, and validates CRC before marking corruption.

State and persistence behavior: Mutation type low 6 bits are the operation, while high bits are wire flags for checksum and accumulative checksum index. Type enum values and reserved slots are protocol/persistence-sensitive. `CommitTransactionRef::serialize()` gates span context handling on protocol versions and contains a tenant-ids TODO retained for older internal paths.

Dependencies and integration points: Depends on FDB types, knobs, tracing, Flow encryption utilities, unit testing, and crc32c. Used by commit proxy requests, TLog messages, global config history, client log events, management configuration writes, and high-contention allocator atomic operations.

Risks: The same byte stores operation and wire flags, so incorrect masking can misclassify operations. Checksum suffix order is strict: checksum first, accumulative index second; deserialization strips in reverse order. Clear-range compaction assumes `keyAfter` form. Changes to enum values or serialization gates require protocol-version and downgrade consideration.

Test signals: Mutation serialization round trips across protocol versions; checksum and accumulative checksum enable/disable cases; corrupt suffix size detection; CRC mismatch detection; single-key clear compact/decompact behavior; operation classification masks; commit transaction span context compatibility; arena lifetime tests.
