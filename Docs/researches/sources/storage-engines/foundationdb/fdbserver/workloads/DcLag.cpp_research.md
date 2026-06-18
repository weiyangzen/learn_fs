# sources/storage-engines/foundationdb/fdbserver/workloads/DcLag.cpp

Purpose: Defines `DcLag`, a gray-failure simulation workload that clogs a primary satellite TLog's outbound communication to remote data-center processes and verifies log routers can detect and recover from data-center lag.

Important APIs/types/functions: `DcLagWorkload`, `clogTlog`, `unclogAll`, `fetchDatacenterLag`, `clogClient`, `StatusClient::statusFetcher`, `RecoveryState`, `fdbSimulationPolicyState().remoteDcId`, and simulator `clogPair`/`unclogPair`.

Control flow: After `startDelay`, client 0 waits for full recovery, finds remote process IPs and primary satellite TLogs, clogs one satellite TLog to each remote IP for the test duration, polls status every five seconds, marks lag detected when seconds approach `LOG_ROUTER_PEEK_SWITCH_DC_TIME`, and unclogs once lag later falls below five seconds.

State and persistence behavior: No database data is written. Runtime state is the list of clogged IP pairs and `lagged` flag. Simulator network state is modified and should be cleaned by `unclogAll` only on the normal recovered path.

Dependencies/integration: It disables `Attrition`, relies on multi-region/satellite log configuration, status JSON `cluster.datacenter_lag`, recovery state updates, and simulator networking.

Risks: If no satellite TLogs exist, the test skips. If the actor times out before recovery, clogged pairs may remain because there is no destructor cleanup. Status field absence causes polling to continue with empty optionals.

Test signals: `DcLagDetected`, `DcLagRecovered`, `DcLagNo*` status traces, and timeout/error wrapping under `DcLagError`.
