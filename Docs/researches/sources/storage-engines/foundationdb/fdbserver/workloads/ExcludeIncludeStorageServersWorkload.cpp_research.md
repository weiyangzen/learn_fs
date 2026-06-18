# sources/storage-engines/foundationdb/fdbserver/workloads/ExcludeIncludeStorageServersWorkload.cpp

Purpose: Creates repeated storage-server exclude/include churn in simulation to exercise RateKeeper bookkeeping when many storage servers leave and rejoin.

Important APIs/types/functions: `ExcludeIncludeStorageServersWorkload`, `workloadMain`, `includeServers`, `excludeServers`, `checkForExcludingServers`, `NativeAPI::getServerListAndProcessClasses`, `logsKey`, `decodeLogsValue`, `dbInfo->logSystemConfig`, `AddressExclusion`, and simulator protected-address checks.

Control flow: Client 0 only, simulation only. Each round first includes everything, then reads storage servers with system-priority lock-aware access, removes protected addresses, TLogs, and log routers from the candidate set, randomly excludes one remaining storage server, and waits up to 100 seconds for exclusion completion. The loop runs 10 to 79 rounds unless too many timeouts or no eligible server exists.

State and persistence behavior: Persistent cluster management state changes through exclusion keys; the workload clears exclusions at the start of each round and at the end to avoid leaving DD stuck. It also sets `allowLogSetKills=false` in simulator policy.

Dependencies/integration: It disables all other failure-injection workloads, depends on server-list and log metadata, data distribution exclusion machinery, and RateKeeper side effects checked by broader simulation validation.

Risks: It can quit early by design when all SS are colocated with TLogs/log routers or exclusions do not finish. It assumes excluding candidates without TLog/log-router roles preserves availability.

Test signals: `WorkloadStart`, `QuitEarlyNoEligibleSSToExclude`, `QuitEarlyNotCompleteServerExclude`, and `WorkloadFinish` with timeout count.
