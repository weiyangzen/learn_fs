<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_bloom.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_bloom.h

Purpose: Declares the legacy plain-table Bloom filter and Bloom block builder used by plain table SSTs.

Important APIs and types: `PlainTableBloomV1` exposes `SetTotalBits`, `AddHash`, `MayContainHash`, `Prefetch`, `GetNumBlocks`, `GetRawData`, `SetRawData`, `GetTotalBits`, and `IsInitialized`. `BloomBlockBuilder` wraps it with `SetTotalBits`, `GetNumBlocks`, `AddKeysHashes`, and `Finish`, plus static meta block name `kBloomBlock`.

Control flow: The inline methods dispatch between locality-aware and no-locality legacy Bloom implementations depending on whether `kNumBlocks` is nonzero. `Prefetch()` only has work in locality mode. The builder is a thin adapter used by plain table construction.

State and persistence: `PlainTableBloomV1` stores total bits, locality block count, probe count, and a raw data pointer. It does not own allocation directly; the allocator passed during setup owns memory. The raw data slice is the persistent filter payload.

Dependencies and integration points: Depends on port cache-line constants, `Slice`, Bloom implementation utilities, hash/math helpers, and logging/allocator types. Plain table reader code can point the Bloom at persisted block bytes using `SetRawData()`.

Risks: The class has `k`-prefixed mutable fields, which can be mistaken for constants. Callers must initialize before adding/testing hashes. Raw data lifetime is external. The format is compatibility-only and lacks newer filter policy abstractions.

Test signals: Initialization assertions, inline may-contain behavior for both modes, prefetch no-op/non-no-op paths, raw data slice size, and `BloomBlockBuilder` output consumed by plain table readers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_bloom.h -->
