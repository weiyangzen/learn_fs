<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionVector.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionVector.h

## Purpose
`VersionVector.h` defines per-storage-tag commit-version vectors used to communicate read freshness and causality information efficiently across sequencer, GRV proxy, client, and storage-server read paths.

## Important APIs, Types, and Functions
`VersionVector` stores a sorted `boost::container::flat_map<Tag, Version>`, `maxVersion`, and a cached encoded size. It exports setters, getters, `clear`, `getDelta`, `applyDelta`, string/compare helpers, encoded-size helpers, custom serialization and deserialization helpers for localities, tag IDs, and version deltas, dynamic serialization traits, and constants `minVersionVector`, `maxVersionVector`, and `invalidVersionVector`.

## Control Flow
Writers set tag versions only with monotonically increasing versions and update `maxVersion`. `getDelta` builds either the entire vector or only entries newer than a reference version based on `CLIENT_KNOBS->SEND_ENTIRE_VERSION_VECTOR`. `applyDelta` ignores invalid or stale deltas and otherwise merges newer entries. Serialization run-length encodes tag localities, compactly chooses tag ID width, delta-encodes commit versions from the minimum, and appends `maxVersion`.

## State and Persistence Behavior
The vector is normally serialized in RPC messages and read-version metadata rather than persisted as standalone database state. Cached encoded size is mutable performance state and invalidated on vector updates. The map must remain ordered because serialization groups consecutive tag localities.

## Dependencies and Integration Points
It depends on Boost flat maps, sets, FDB types, and client knobs. It integrates with `StorageServerInterface` read requests, commit/read-version propagation, storage freshness checks, and GRV proxy optimization.

## Risks and Edge Cases
`operator==` compares only `maxVersion`, while `compare` checks full map equality; callers must choose intentionally. Serialization assumes ordered tags and trusted buffer sizes. `applyDelta` only merges entries with version greater than current `maxVersion`, which matches delta semantics but would drop a tag-specific update lower than global max. Cached size assertions can expose stale invalidation bugs.

## Test Signals
Signals include version-vector unit tests for delta/apply behavior, serialization round trips with mixed localities and tag ID widths, read freshness tests, GRV proxy/client tests, and knob coverage for sending entire vectors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/VersionVector.h -->
