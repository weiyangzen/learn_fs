# sources/storage-engines/tikv/components/resource_control/src/service.rs

## Purpose
`service.rs` connects the in-memory `ResourceGroupManager` to PD metadata and reporting RPCs. It loads and watches resource-group definitions from meta storage, loads RU controller cost configuration, and periodically reports background RU consumption to PD.

## Important APIs, Types, And Functions
`ResourceManagerService` owns the manager, an `RpcClient`, a checked/sourced meta-storage client, and the latest watch revision. `new` wires meta storage to the resource-control source. `watch_resource_groups` performs initial reload, then starts a prefixed watch from the stored revision and applies put/delete events. `reload_all_resource_groups` performs a full prefixed get, parses protobuf groups, adds valid groups, retains only groups still present, and updates `revision`.

`load_controller_config` repeatedly reads `RESOURCE_CONTROL_CONTROLLER_CONFIG_PATH` and parses `ControllerConfig` JSON into `RequestUnitConfig`. `report_ru_metrics` samples the shared background limiter every five seconds, computes deltas from the last report, converts CPU and IO usage to RRU/WRU using controller config, and calls `pd_client.report_ru_metrics`.

## Control Flow
Startup calls `watch_resource_groups`, which first reconciles all current groups and then watches for incremental changes. Watch compaction triggers a full reload. Transient errors sleep for `RETRY_INTERVAL` and restart the watch. Reporting waits until background groups exist, then reads limiter statistics, skips unchanged samples, builds a `TokenBucketsRequest` under the default resource group with `is_background = true`, and sends it to PD.

## State And Persistence Behavior
Persistent source of truth is PD meta storage. Local service state is only the last watch revision and previous background statistic snapshot. The report loop resets nothing in the limiter; it sends deltas by subtracting previous cumulative counters and resets its baseline when the limiter version changes.

## Dependencies And Integration Points
The file integrates with `pd_client` meta storage and RPC reporting, `kvproto` resource-manager messages, serde JSON controller config, `GLOBAL_TIMER_HANDLE` delays, and `ResourceGroupManager`. Background limiter statistics come from `resource_limiter::GroupStatistics`.

## Risks
The watch loop is intentionally infinite; bad data logs parse errors but leaves previous valid local state until a retain pass. `load_controller_config` blocks forever until valid config exists. Reporting all background consumption under `DEFAULT_RESOURCE_GROUP_NAME` matches the shared-limiter design but loses per-background-group attribution. Delta subtraction assumes monotonic counters and handles limiter replacement only through `version`.

## Test Signals
Tests use mock PD meta storage to validate CRUD reload, watch put/delete updates, watch-server reboot recovery, controller config loading, and background RU reporting with failpoint-shortened report intervals.
