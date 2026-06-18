# sources/storage-engines/foundationdb/fdbclient/CommitProxyInterface.cpp

## Purpose

`CommitProxyInterface.cpp` supplies explicit template instantiations for client/commit-proxy network types and implements backup mutation chunk helper functions used to split large mutation payloads.

## Important APIs And Functions

The file instantiates `ReplyPromise<ClientDBInfo>`, `ReplyPromise<CachedSerialization<ClientDBInfo>>`, `NetNotifiedQueue<OpenDatabaseCoordRequest, true>`, `ReplyPromise<GetKeyServerLocationsReply>`, and `NetSAV<GetKeyServerLocationsReply>`. These force template code generation in this translation unit for RPC and network serialization types declared in headers.

`getBackupKey(BinaryWriter& wr, uint32_t** partBuffer, int part)` appends or mutates a big-endian part number at the end of a serialized mutation key. The first call serializes `part` and records a pointer to the part field inside the writer buffer; later calls rewrite the pointed-to field without rebuilding the whole key. `getBackupValue(Key& content, int part)` returns a `StringRef` slice of `content` for the requested part using `CLIENT_KNOBS->MUTATION_BLOCK_SIZE`.

## Control Flow

The backup-key helper has two modes: initialize the part suffix and pointer, then update in place for subsequent parts. The value helper computes offset and length with `std::min()` so the last block can be smaller than the block size.

## State And Persistence

No durable state is stored here. The only mutable state is the caller-owned `BinaryWriter` buffer and `partBuffer` pointer. The resulting keys and values are used by backup/commit paths that persist split mutation content elsewhere.

## Dependencies And Integration Points

The file includes `CommitProxyInterface.h`, `CoordinationInterface.h`, and uses `CLIENT_KNOBS`. It integrates with RPC serialization and backup mutation block storage.

## Risks And Test Signals

The pointer returned through `partBuffer` is valid only while the writer buffer is not reallocated; callers must not append in ways that invalidate it after caching the pointer. Tests should cover multi-part mutation key generation, big-endian ordering, exact block boundaries, and final short block slicing.
