# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/DatabaseConfiguration.h

Purpose: Defines the in-memory and serialized database configuration model used to interpret system configuration keys for proxies, resolvers, logs, storage, regions, satellites, backup workers, storage migration, encryption, exclusions, and policies.

Important APIs/types/functions: `SatelliteInfo` and `RegionInfo` describe region/satellite priorities and satellite TLog replication/quorum policies. `DatabaseConfiguration` applies mutations, sets/clears/gets options, validates configuration, serializes raw sorted config, converts to string/JSON/configure command, derives desired component counts, computes required datacenters/zones and tolerated failures, checks exclusions, and resolves auto counts. Public fields expose all major configured values, policies, store types, migration/encryption modes, regions, and backup/perpetual wiggle settings.

Control flow: Configuration key-values are loaded via `fromKeyValues()` or serialized raw config, then `setInternal()` populates derived fields and policies. Mutations from the system keyspace are applied with `applyMutation()`. Before serialization/comparison, mutable maps are made immutable into sorted `rawConfiguration`; on deserialization, raw entries are replayed through `setInternal()` and defaults are restored.

State and persistence behavior: The durable representation is sorted `rawConfiguration` key-values from system config keys. Enums such as store type, TLog version, spill type, storage migration, and deprecated encryption mode are persisted via stable numeric values. Auto counts use `-1` sentinel to select computed auto values.

Dependencies and integration points: Depends on FDB types, commit mutations, replication policies, and status. Used by cluster controller, management configure APIs, recruitment, DD, log system, storage server exclusion, status output, and recovery validation.

Risks: Config validation spans many subsystems, so accepting an inconsistent policy can make recruitment/recovery impossible. Serialization mutates internal representation by freezing mutable config. Persisted enum numeric values must never be reordered. Region and satellite quorum math is availability-critical. Exclusion checks must match locality/address semantics.

Test signals: Build/apply/serialize round trips from config key-values; configure JSON/string conversion; validity checks for replication, regions, store types, backup options, and migration modes; desired count auto override tests; region/satellite quorum and failure tolerance tests; exclusion matching; upgrade tests for persisted enum values.
