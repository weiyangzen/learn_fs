# sources/storage-engines/foundationdb/fdbserver/core/FDBSimulationPolicy.cpp

## Purpose
Installs and maintains FoundationDB-specific simulation fault policy. It controls whether simulated process kills, corruption, storage replica fault injection, and datacenter death are allowed under the current database replication configuration.

## Important APIs, Types, and Functions
- `stringToFDBExtraDatabaseMode()` parses configuration strings into `FDBExtraDatabaseMode`.
- `FDBSimulationPolicy` implements `ISimulationPolicy` methods: `datacenterDead()`, `shouldRunVersionValidation()`, `canSwapToMachine()`, `checkInjectedCorruption()`, `hasCapability()`, and `canKillProcesses()`.
- `installFDBSimulationPolicy()` registers the policy with `g_simulator`.
- `fdbSimulationPolicyState()` returns the singleton mutable policy state.
- `updateFDBSimulationPolicy()` refreshes policy state from `DatabaseConfiguration`.
- `setFDBSimulationPolicyRemoteTLogPolicy()` overrides remote TLog policy.

## Control Flow
Policy decisions derive locality groups for alive/dead processes and validate them against storage, TLog, remote TLog, and satellite replication policies. `canKillProcesses()` may downgrade dangerous kill types to reboot-style actions if too many processes are dead, not enough would remain, or auto-configuration would lack coordinator quorum across unique machines. Capability checks expose TSS/fault-injection modes to simulation components.

## State and Persistence Behavior
All state is process-local singleton `FDBSimulationPolicyState`. It stores replication policies, region IDs, satellite IDs, TSS mode, corrupt worker map, desired coordinator count, extra database mode, and flags such as `allowLogSetKills`. No persistent cluster state is written.

## Dependencies and Integration Points
Depends on simulator interfaces, replication policy utilities, locality data, `DatabaseConfiguration`, and simulator process info. It is installed into the global simulator and is consulted by fault injection, process killing, version validation, and corruption paths.

## Risks and Edge Cases
The safety logic is highly configuration-sensitive, especially with usable regions, remote TLogs, satellite fallback policies, and write anti-quorums. Unique-machine quorum checks can change kill type even when replication policies appear satisfied. Extra databases disable version validation and machine swapping. Unknown extra database mode strings log and assert.

## Test Signals
No embedded unit tests. Simulation workloads that vary replication modes, kill types, satellite settings, TSS modes, and process localities are the relevant coverage.
