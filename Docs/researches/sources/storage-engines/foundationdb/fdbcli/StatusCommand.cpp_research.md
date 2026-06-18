# sources/storage-engines/foundationdb/fdbcli/StatusCommand.cpp

Purpose: Implements `status`, rendering FoundationDB cluster status in normal, detailed, minimal, or JSON form from status JSON.

Important APIs/types/functions: Helpers include `getCoordinatorsInfoString`, `lineWrap`, `getNumOfNonExcludedProcessAndZones`, `getNumofNonExcludedMachines`, `logEpochsMayBeLosingData`, `getDateInfoString`, `getProcessAddressByServerID`, `getWorkloadRates`, `getBackupDRTags`, and `logBackupDR`. Public functions include `toBytesString`, `printStatus`, `statusCommandActor`, `statusGenerator`, and `CommandFactory statusFactory`. It uses `StatusObjectReader`, `StatusClient::StatusLevel`, `StatusClient::statusFetcher`, and the special key `\xff\xff/status/json`.

Control flow: `statusCommandActor` selects the output level from tokens, reads status JSON via the multiversion transaction special key when valid or native `StatusClient::statusFetcher` fallback otherwise, parses it, and calls `printStatus`. `printStatus` first handles incompatible outgoing connections, then branches by level. Normal/detailed mode builds one large output string: client/coordination messages, fatal recovery diagnostics, configuration, cluster counts/fault tolerance/server time, data health/size/movement, storage wiggle, operating space, workload, backup/DR, and detailed per-process performance/coordination sections. Minimal mode prints availability/health and cluster-file freshness. JSON mode pretty-prints the raw object.

State and persistence behavior: Read-only. All state is derived from live status JSON and Flow transport compatibility flags. No local or cluster writes.

Dependencies and integration points: Deeply coupled to status JSON schema paths from cluster, client, process, machine, workload, backup, DR, fault tolerance, and QoS subsystems. Also integrates with fdbcli exec mode formatting and command completion.

Risks: Large schema-dependent renderer with many try/catch blocks; missing fields generally degrade to "unknown" or section failure, but some paths can still assume objects exist, such as later use of `processesMap.obj()`. `getNumofNonExcludedMachines` appears to count machines where `excluded` exists and is false, not machines without an excluded field, which may undercount depending on schema. `getDateInfoString` uses localtime and is not timezone-stable in tests. Normal mode can hide messages during fatal recovery based on skip lists.

Test signals: Golden-output tests should cover minimal healthy/unavailable/issues, JSON output, normal and detailed status with unreachable coordinators, fatal recovery states, exclusions, regions/TSS, data loss warnings, DD disabled warnings, backup/DR tags, process performance details, missing/malformed sections, and cluster-file freshness warnings.
