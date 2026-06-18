# sources/storage-engines/foundationdb/fdbserver/workloads/GcGenerations.cpp

Purpose: Tests that with TLog recovery tracking enabled, old TLog generations can be garbage-collected during recovery before the database reaches fully recovered.

Important APIs/types/functions: `GcGenerationsWorkload`, `clogRemoteDc`, `unclogAll`, `dbAvailable`, `generateMultipleTxnGenerations`, `gcGenerationsTestClient`, simulator connection failures, `disableTLogRecoveryFinish`, `logSystemConfig.oldTLogs`, `RecoveryState`, and `getConnectionString`.

Control flow: Client 0 waits `startDelay` and database availability, disables TLog recovery finish, partitions the remote DC from non-remote processes except coordinators, repeatedly enables connection failures, waits for accepting commits, ensures the master is in the primary DC, reboots it to generate old TLog generations, and verifies generation count grows. Then it unclogs, disables connection failures, re-enables recovery finish, repeatedly reboots the master until old generations shrink to at most one, and finally waits for full recovery.

State and persistence behavior: No user key writes occur. Simulator network partition state, connection-failure state, process reboot state, and global simulation policy are mutated. Destructor cleanup unclogs, disables connection failures, and resets `disableTLogRecoveryFinish`.

Dependencies/integration: Disables `Attrition` and `RandomClogging`, relies on remote DC locality, log-system recovery state, coordinator resolution, master election behavior, and TLog generation GC internals.

Risks: Highly timing-sensitive and simulation-only. Remote masters are rebooted while partitioned to force primary-DC coordination; after unclogging the guard is intentionally relaxed. Failure to clean simulator state would damage later workloads, hence explicit destructor cleanup.

Test signals: `PartitionRemoteDc`, `CurrentGenerations`, `AfterMultipleRecovery`, `RebootMasterForGC`, `GcGenerationsWaitingForReduction`, and `GcGenerationsWorkloadFinish`.
