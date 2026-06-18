# sources/storage-engines/foundationdb/fdbclient/SystemData.cpp

## Purpose
`SystemData.cpp` defines FoundationDB's system key constants and the encoding/decoding helpers for metadata stored in those keyspaces. It is a compatibility-critical registry for shard ownership, storage server metadata, server tags, audit/checkpoint/data-move state, process and worker records, backup/restore metadata, bulk load/dump, range locks, throttling keys, global configuration keys, and transaction/system markers.

## Important APIs, types, and functions
Global `KeyRef` and `KeyRangeRef` constants define normal, system, special, metadata, configuration, backup, audit, tag, server, bulk, and lock keyspaces. Helper families include `keyServersKey()`, `keyServersValue()`, `decodeKeyServersValue()`, audit key/value helpers, checkpoint and data-move helpers, log value helpers, server key helpers, `newDataMoveId()` and `decodeDataMoveId()`, TSS quarantine helpers, server tag helpers, datacenter/tLog helpers, server list and software version serialization, process/worker/backup helpers, log range helpers, construct value helpers, and healthy-zone helpers. `SystemKey::SystemKey()` checks prefix conflicts in simulation.

## Control flow
Most functions are deterministic encoders or decoders around `BinaryWriter`, `BinaryReader`, `ObjectWriter`, and `ObjectReader`. Compatibility branches inspect serialized protocol versions to support older `keyServersValue`, shard metadata IDs, and tag-encoded layouts. Decoders usually clear output vectors, parse values, map tags back to UIDs using either a `RangeResult` or a `std::map<Tag, UID>`, sort server IDs, and assert or trace when required mappings are missing. Data-move IDs encode data-move type and reason in low bits of the UID second half while preserving special values for anonymous, empty, and unassigned shards.

## State and persistence behavior
This file is almost entirely about persisted state. The constants are database key contracts. Values encode protocol-versioned binary or object-serialized data for cluster metadata. Mutating these formats can affect upgrades, downgrades, recovery, data distribution, backup/restore, bulk operations, and storage server recruitment. The simulation-only `SystemKey` known-key set tracks prefix conflicts in process memory to catch accidental overlapping system key definitions.

## Dependencies and integration points
Dependencies include `KeyBackedTypes`, `SystemData.h`, `FDBTypes`, `StorageServerInterface`, Flow arenas/serialization/unit tests, and protocol-version feature flags. Integration points span data distribution, storage servers, coordinators, backup agents, audit, TSS, bulk load/dump, global configuration, metrics, and client management APIs.

## Risks and edge cases
This file has high upgrade risk because key names, ranges, and binary layouts are durable contracts. Prefix overlap can route scans incorrectly; simulation catches only keys constructed through `SystemKey`. Version-specific decoding paths must preserve behavior for legacy values. Tag-to-UID decoding can assert when a tag map is incomplete. `decodeDataMoveId()` tolerates out-of-scope type/reason values with warnings for upgrade compatibility, but this can affect fetch throttling or physical shard move choices. Several encode functions use string forms, big-endian values, or object serializers, so byte-order and protocol flags are part of the contract.

## Test signals
Local tests cover storage server interface serialization, key server value compatibility, and data move ID encoding/decoding. Additional signals should include upgrade/downgrade fixture tests for all protocol-versioned value formats, prefix-range overlap checks, tag mapping failure tests, and end-to-end tests through data distribution, backup/restore, audit, bulk load/dump, and TSS quarantine flows.
