# sources/storage-engines/foundationdb/fdbserver/workloads/ConfigureDatabase.cpp

## Purpose
`ConfigureDatabase.cpp` defines `ConfigureDatabase`, a randomized configuration-change workload. It changes redundancy, regions, roles, coordinators, storage engine, log engine/version/spill options, backup worker configuration, and storage migration settings, then optionally waits for storage servers to converge to the configured store type.

## Important APIs, Types, And Functions
Top-level helpers include `generateRegions`, `IssueConfigurationChange`, `valueToUInt64`, `getDatabaseName`, `issueAggressiveMigrationIfNeeded`, `randomRoleNumber`, and `singleDB`. Constants define candidate storage migration strings, log strings, redundancy modes, and backup-worker modes. The workload uses `ManagementAPI::changeConfig`, `changeQuorum`, `autoQuorumChange`, `nameQuorumChange`, `getDatabaseConfiguration`, `getStorageServers`, `ParsePerpetualStorageWiggleLocality`, and storage server `getKeyValueStoreType`.

## Control Flow
`setup` first forces `"single storage_migration_type=aggressive"`. `start` records current configuration, excludes sharded RocksDB when shard-encoded metadata is off, and client 0 runs `singleDB` until timeout. `singleDB` loops through randomized choices: wait/read recovery, delay, issue redundancy/region/role config, change quorum/name, change storage engine, change log settings, change backup worker setting, or change storage migration/perpetual wiggle settings. `check` optionally loops until storage servers report the configured store type or triggers aggressive migration if topology cannot support gradual wiggle.

## State And Persistence
Persistent state is cluster configuration and coordinator/quorum descriptor state. Storage migration settings can cause actual storage-engine migration and perpetual wiggle behavior. Metrics persist only in the workload's `retries` counter, though the loop does not visibly increment it in this file.

## Dependencies And Integration Points
The workload depends on management API configuration parsing, simulation policy datacenter topology, satellite/remote redundancy options, process locality, storage migration support, and storage server interfaces. It disables `Attrition` because random process failures can make configuration convergence checks unstable.

## Risks
Randomly generated config strings can be invalid by design, so callers must tolerate management errors from impossible configurations. The workload factory variable is named `DestroyDatabaseWorkloadFactory` even though it registers `ConfigureDatabaseWorkload`, which is confusing but legal. Storage engine exclusion depends on option values and shard encoding state. The storage convergence loop can run for a long time when migration is slow or topology cannot provide replacement teams; aggressive migration is a mitigation for small DCs.

## Test Signals
Trace events include `ConfigureDatabase_Config`, `ConfigureDatabase_WrongStoreType`, `ConfigureTestSettingWiggleLocality`, and printed `Issuing configuration change:` lines. Metrics expose `Retries`, but most correctness signals are management errors, storage-type convergence, and later `ConsistencyCheck` workloads.
