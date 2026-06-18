# sources/storage-engines/foundationdb/fdbserver/core/SeedShardServers.cpp

## Purpose
`SeedShardServers.cpp` seeds a brand-new database's storage-server metadata and initial shard ownership into a `CommitTransactionRef`. It assigns tags, stores server list and metadata records, initializes `keyServers`, and marks every storage server as owning `allKeys`.

## Important APIs, types, and functions
- `seedShardServers(Arena&, CommitTransactionRef&, std::vector<StorageServerInterface>)` is the only function.
- It uses tag locality helpers (`tagLocalityListKeyFor`, `tagLocalityListValue`, `serverTagKeyFor`, `serverTagValue`), server list helpers, `KeyBackedObjectMap` for storage metadata, `keyServersValue`, `serverKeysValue`, and KRM seeding via `krmSetPreviouslyEmptyRange`.

## Control flow
The function first groups storage servers by `dcId`, assigning each locality a tag locality id and then sequential tag ids within that locality. It sorts servers for deterministic output, forces the transaction to be the first transaction by setting `read_snapshot = 0` and adding an `allKeys` read conflict, then writes per-server tag/list/metadata keys. It builds parallel vectors of tags and server UIDs and initializes `keyServers` and each server's `serverKeys`.

If shard-encoded location metadata is enabled, it creates a new shard/data-move id with `DataMovementReason::SEED_SHARD_SERVER`, writes `keyServers` with source server ids and shard id, and stores `serverKeysValue(shardId)` for each server. Otherwise it writes legacy tag-encoded or UID-encoded `keyServers` values and `serverKeysTrue`.

## State and persistence behavior
The function writes system metadata into the passed commit transaction but does not commit itself. It writes tag locality list entries, server tag entries, server list entries, storage metadata entries, optional TSS identity mappings, `serverMetadataChangeKey`, the all-key `keyServers` range, and all-key `serverKeys` ranges for every server.

## Dependencies and integration points
It depends on system key encoders, `KeyBackedTypes`, `KeyRangeMap`, storage server interfaces, DD/data-move id helpers, and `SERVER_KNOBS`/`CLIENT_KNOBS` feature flags. It is part of initial cluster/database construction and must align with later `MoveKeys.cpp` assumptions about `keyServers` and `serverKeys`.

## Risks and edge cases
Tag locality ids are `int8_t`, so unexpected numbers of distinct DC ids would be risky. The `TSS_HACK_IDENTITY_MAPPING` branch logs severity error and is explicitly test-only behavior. The initial all-keys assignment differs by `TAG_ENCODE_KEY_SERVERS` and `SHARD_ENCODE_LOCATION_METADATA`, so mixed-version or knob-transition scenarios need careful compatibility handling.

## Test signals
There are no local tests. Validation comes from successful cluster bootstrap, correct initial `serverList`/`serverTag`/`keyServers`/`serverKeys` contents, and `TSSIdentityMappingEnabled` traces if the test-only knob is enabled.
