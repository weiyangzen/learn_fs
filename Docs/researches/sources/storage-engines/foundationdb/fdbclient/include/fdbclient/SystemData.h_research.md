<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SystemData.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SystemData.h

## Purpose
`SystemData.h` documents and declares the reserved `\xff` system keyspace layout for FoundationDB. It provides constants plus encode/decode helpers for shard placement, server metadata, configuration, backup, restore, bulk load, bulk dump, audit, range locks, tag throttling, global configuration, and many cluster-control records.

## Important APIs, Types, and Functions
Important declarations include key ranges such as `normalKeys`, `systemKeys`, `specialKeys`, `keyServersKeys`, `serverKeysRange`, `serverListKeys`, `serverTagKeys`, `configKeys`, backup ranges, bulk load/dump ranges, range lock ranges, tag throttle ranges, log/apply mutation ranges, and many singleton keys. Helper functions encode and decode key server values, server keys, server tags, process classes, worker lists, checkpoint state, audit state, data moves, bulk load/dump state, range lock state, backup metadata, healthy zones, and exclusion/failure entries.

## Control Flow
Cluster components use the declared constants to build transaction key ranges and use matching encode/decode helpers to convert typed metadata into `Value` records. Data distribution reads `keyServers` and `serverKeys` mappings, storage recruitment writes `serverList` and `serverTag` keys, configuration code mutates `conf` keys, backup and restore code manages its reserved prefixes, and management commands update exclusion, failure, and locking keys.

## State and Persistence Behavior
Nearly every declaration maps to durable system-key state. Some keys are watched or changed as version signals, such as metadata changes, process class changes, excluded server version keys, tag throttle signal keys, and backup partition request keys. The header itself only declares constants and helpers, but it is the contract for persistent cluster metadata and therefore has strict compatibility implications.

## Dependencies and Integration Points
It depends on checksums, bulk loading/dumping, `FDBTypes`, range locks, and `StorageServerInterface`. It is included by storage, data distribution, cluster controller, master/proxy, backup/restore, CLI, status, and administrative code that needs to read or mutate system keys.

## Risks and Edge Cases
Key-prefix changes are high risk because older binaries, recovery, and downgrade paths may depend on exact layouts. The header includes `StorageServerInterface.h`, while that header includes `SystemData.h` indirectly through other files in some paths, so include-order discipline matters. Encode/decode helpers must match the on-disk format exactly. Plain `extern` declarations hide implementation details in `.cpp` files, so tests need to cover runtime values, not just compilation.

## Test Signals
Signals include system-key encode/decode unit tests, simulation recovery tests, data distribution movement tests, configuration mutation tests, backup/restore integration tests, CLI exclusion/failure tests, bulk load/dump tests, and downgrade/upgrade serialization compatibility checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SystemData.h -->
