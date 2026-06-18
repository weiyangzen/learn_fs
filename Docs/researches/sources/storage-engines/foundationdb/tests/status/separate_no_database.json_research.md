<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_no_database.json -->
# sources/storage-engines/foundationdb/tests/status/separate_no_database.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_no_database` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `fault_tolerance`, `machines`, `messages`, `processes`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=False, healthy=False, coordinators=coordinators=[address='127.0.0.1:4701', reachable=True, address='127.0.0.1:4703', reachable=True, address='127.0.0.1:4704', reachable=True], quorum_reachable=True, recovery_state=description='The coordinator(s) have no record of this database. Either the coordinator addresses are incorrect, the coordination state on those machines is missing, or no database has been created.', name='configuration_never_created', data_state=absent, processes=3, machines=1.
Configuration snapshot: coordinators_count=3, excluded_servers=[]. Fault tolerance snapshot: max_zone_failures_without_losing_availability=0, max_zone_failures_without_losing_data=0.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
message names must remain stable: `cluster:unreadable_configuration`, `cluster:transaction_start_timeout`, `cluster:commit_timeout`, `cluster:status_incomplete`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=False, healthy=False, quorum_reachable=True, messages=cluster:unreadable_configuration, cluster:transaction_start_timeout, cluster:commit_timeout, cluster:status_incomplete, recovery=configuration_never_created.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_no_database.json -->
