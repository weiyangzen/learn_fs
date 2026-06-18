# sources/storage-engines/foundationdb/fdbserver/workloads/ClogTlog.cpp

## Purpose
`ClogTlog.cpp` defines `ClogTlog`, a simulation gray-failure/recovery workload. It partitions or heavily clogs one primary TLog from all non-CC server processes, waits for recovery to leave `FULLY_RECOVERED`, and either relies on gray failure or force-excludes the bad TLog if recovery stalls.

## Important APIs, Types, And Functions
The workload uses `ServerDBInfo`, `RecoveryState`, `ManagementAPI::changeConfig`, simulator `clogPair`, `disconnectPair`, `unclogPair`, and `reconnectPair`. Core methods are `clogTlog`, `unclogAll`, `excludeFailedLog`, and `clogClient`.

## Control Flow
Client 0 in simulation runs under a timeout. `clogClient` may choose true disconnection instead of clogging, waits for other workloads to issue transactions and for full recovery, then calls `clogTlog` until near test end. `clogTlog` selects a primary local TLog not on the cluster controller IP and clogs/disconnects it in both directions with all other non-tester IPs except CC. Once recovery starts, `clogClient` either lets gray failure recover the cluster or starts `excludeFailedLog`, which force-excludes the TLog after 30 seconds without recovery progress. The actor succeeds when `dbInfo` returns to `FULLY_RECOVERED`, then unclogs all recorded pairs.

## State And Persistence
Persistent cluster state may include a forced `exclude=IP:PORT` configuration change. Runtime state includes the selected TLog, clog/disconnect pairs, `useDisconnection`, and simulator network rules.

## Dependencies And Integration Points
The workload depends on primary TLog recruitment state, cluster controller reachability, management API exclusion, simulator networking, and recovery state transitions. It is explicitly targeted at a recovery bug where a partitioned TLog could be rerecruited and stall initialization.

## Risks
The selected `tlog` is the first eligible TLog discovered and is not randomized among all eligible logs. When `useGrayFailureToRecover` is true, `excludeFailedLog` is disabled and the test relies entirely on gray failure before timeout. Failure reporting is trace-based because `check` returns true; timeout logs `ClogTLogFailure` but does not return false directly.

## Test Signals
Trace events include `ClogTlog`, `ClogTLogUseGrayFailreToRecover`, `ExcludeFailedLog`, `ClogDoneFullyRecovered`, and `ClogTLogFailure`. Recovery-state transitions and absence of stuck recovery are the meaningful signals.
