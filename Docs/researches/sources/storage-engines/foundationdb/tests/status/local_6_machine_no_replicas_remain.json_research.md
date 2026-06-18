<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/local_6_machine_no_replicas_remain.json -->
# sources/storage-engines/foundationdb/tests/status/local_6_machine_no_replicas_remain.json

## Purpose
Golden FoundationDB status JSON fixture for the `local_6_machine_no_replicas_remain` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `fault_tolerance`, `latency_probe`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=True, healthy=False, coordinators=coordinators=[address='10.0.3.1:9191', reachable=True], quorum_reachable=True, recovery_state=description='Recovery complete.', name='fully_recovered', data_state=description='No replicas remain of some data', healthy=False, min_replicas_remaining=0, name='missing_data', processes=3, machines=3.
Configuration snapshot: coordinators_count=1, excluded_servers=[], redundancy=factor='triple', storage_engine='memory'. Fault tolerance snapshot: max_zone_failures_without_losing_availability=0, max_zone_failures_without_losing_data=0.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
fixture represents unhealthy/unavailable state and should not be normalized as success; data state carries scenario-specific health semantics

## Test Signals
Expected signals include availability=True, healthy=False, quorum_reachable=True, messages=none, recovery=fully_recovered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/local_6_machine_no_replicas_remain.json -->
