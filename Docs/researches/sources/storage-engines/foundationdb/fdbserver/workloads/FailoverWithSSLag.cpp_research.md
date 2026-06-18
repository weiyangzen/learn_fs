# sources/storage-engines/foundationdb/fdbserver/workloads/FailoverWithSSLag.cpp

Purpose: Tests that regional failover does not complete while remote storage servers lag behind primary, even if remote TLogs are in sync.

Important APIs/types/functions: `FailoverWithSSLagWorkload`, `findAndClogRemoteStorages`, `clogUnclogRemoteStorages`, `fetchStorageServerLag`, `waitForRemoteDataCenterToLag`, `failover`, `doFailover`, `ManagementAPI::changeConfig`, `waitForPrimaryDC`, `StatusClient`, and simulator `clogPair`.

Control flow: In simulation, client 0 sets usable regions to two, waits for full recovery, finds remote TLog IPs and remote storage process IPs, clogs TLog/storage communication both ways, waits until storage lag exceeds `MAX_VERSION_DIFFERENCE`, starts failover by disabling the primary, and races failover completion against a 100 second delay. If failover completes while clogged, the test fails; otherwise it unclogs and expects failover to complete with lag below threshold.

State and persistence behavior: No user data is written. Cluster configuration changes via `changeConfig` and simulator network clogs are the main state changes. Runtime `testSuccess` records failure.

Dependencies/integration: Disables all failure injection, depends on multi-region simulation, status JSON lag fields, recovery state, log-system config, remote DC locality, and management config strings from simulation policy.

Risks: Missing remote TLogs or storages marks failure. Clogged connections are not cleaned in a destructor. Status lag fields are required; absence causes indefinite waiting.

Test signals: `SSLag`, `LagInfo`, `FailoverBegin`, `FailoverComplete`, failure by `testSuccess=false`, and `FailoverWithSSLagError`.
