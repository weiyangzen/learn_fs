# sources/storage-engines/foundationdb/fdbserver/datadistributor/SimulatedCluster.cpp

Purpose: builds a minimal `BasicSimulationConfig` from `BasicTestConfig` for datadistributor and mock-global-state tests. It translates replication intent and optional role counts into a `DatabaseConfiguration` plus a simple machine/process layout.

Important APIs and functions: `generateBasicSimulationConfig()` is the exported function. Private helpers `getRedundancyMode()` maps minimum replication to `single`, `double`, or `triple`; `applyConfigurationString()` uses FoundationDB management parsing to fill the database config.

Control flow: generation chooses datacenter count from `singleRegion`, `simpleConfig`, and minimum replication, applies the redundancy mode, optionally forces simplified proxy/resolver/TLog counts, applies explicit overrides, sets `storageTeamSize`, applies log anti-quorum when provided, sets usable regions for single-DC configs, and computes a default or overridden machine count large enough for the storage team.

State and persistence: no persistent state. It returns a value object containing topology counts and `DatabaseConfiguration`.

Dependencies and integration: depends on `BasicTestConfig`/`BasicSimulationConfig` from `SimulatedCluster.h`, `DatabaseConfiguration`, and `buildConfiguration()` from the generic management API. `MockGlobalState` uses the result to create process locality and seed storage servers.

Risks: the helper is intentionally simplified and does not model all production simulation knobs. The redundancy string mapping is coarse; unusual replication policies or multi-region layouts need explicit extensions. Assertions assume `buildConfiguration()` recognizes the selected mode.

Test signals: indirectly exercised by `MockGlobalState.cpp` tests that call it before cluster initialization. Focused tests could validate simple versus multi-DC machine counts, override precedence, and ASAN-specific machine-count behavior if that field is later consumed here.
