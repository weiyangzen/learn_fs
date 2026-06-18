# sources/storage-engines/foundationdb/fdbserver/workloads/ClogRemoteTLog.cpp

## Purpose
`ClogRemoteTLog.cpp` defines `ClogRemoteTLog`, a simulation-only gray-failure workload for remote log topologies. It degrades connectivity between a selected remote TLog and most server processes, observes storage-server data lag and log exclusion, and verifies status JSON exposes gray-failure information when exclusion occurs.

## Important APIs, Types, And Functions
Key elements are `TestState`, `StatePath`, `measureMaxSSLag`, `statusError`, `statusIncomplete`, `grayFailureStatusCheck`, `getRemoteSSIPs`, `getRemoteTLogs`, `clogRemoteTLog`, `remoteTLogNotInDbInfo`, and `workload`. It uses `StatusClient::statusFetcher`, `NativeAPI::getServerListAndProcessClasses`, `ServerDBInfo`, `logSystemConfig.tLogs`, and simulator `clogPair`.

## Control Flow
Only client 0 in simulation runs. `workload` starts `clogRemoteTLog`, records `TEST_INIT`, then periodically measures max storage-server lag. `clogRemoteTLog` waits for full recovery, selects an isolated remote TLog if possible, finds remote storage-server IPs, and clogs that remote TLog against non-tester/non-CC processes for most of the test duration. The monitor records transitions between normal/high storage lag and `CLOGGED_REMOTE_TLOG_EXCLUDED` when the selected remote TLog disappears from `dbInfo` while commits are accepted. `check` compares the actual path to allowed expected paths unless buggify or insufficient isolation disables strict checking.

## State And Persistence
No database writes are performed. State lives in simulator network clog rules, `actualStatePath`, `cloggedRemoteTLog`, and `doCheck`. Status JSON is read repeatedly but not persisted by the workload.

## Dependencies And Integration Points
The workload requires simulated multi-region/remote-log configuration, storage-server status fields with `data_lag`, cluster `gray_failure` status JSON, the simulation policy remote DC id, and accurate `ServerDBInfo` log system state.

## Risks
If no isolated remote TLog exists, the workload still clogs a random remote TLog but relaxes the final check. Status collection can be incomplete during recovery; `grayFailureStatusCheck` treats incomplete status as retryable but asserts if a complete status lacks `gray_failure`. Expected state paths are necessarily timing-sensitive because lag may recover, stay high, or be superseded by exclusion.

## Test Signals
Trace events include `SSDataLag`, `MaxSSDataLag`, `ClogRemoteTLog`, `ClogRemoteTLogMoreInfo`, `GrayFailureStatus`, `GrayFailureStatusIncomplete`, `NoGrayFailure`, `ClogRemoteTLogCheck`, and `ClogRemoteTLogCheckFailed`. The final state-path match is the primary pass/fail condition.
