<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_cannot_write_cluster_file.json -->
# sources/storage-engines/foundationdb/tests/status/separate_cannot_write_cluster_file.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_cannot_write_cluster_file` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `fault_tolerance`, `latency_probe`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=True, healthy=False, coordinators=coordinators=[address='127.0.0.1:4701', reachable=True, address='127.0.0.1:4703', reachable=True, address='127.0.0.1:4704', reachable=True], quorum_reachable=True, recovery_state=description='Recovery complete.', name='fully_recovered', data_state=healthy=True, name='healthy', processes=3, machines=1.
Configuration snapshot: coordinators_count=2, excluded_servers=[], redundancy=factor='single', storage_engine='memory'. Fault tolerance snapshot: max_zone_failures_without_losing_availability=0, max_zone_failures_without_losing_data=0.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
message names must remain stable: `client:inconsistent_cluster_file`, `cluster:client_issues`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=True, healthy=False, quorum_reachable=True, messages=client:inconsistent_cluster_file, cluster:client_issues, recovery=fully_recovered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_cannot_write_cluster_file.json -->
