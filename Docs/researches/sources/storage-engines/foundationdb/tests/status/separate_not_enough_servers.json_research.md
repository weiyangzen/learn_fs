<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_not_enough_servers.json -->
# sources/storage-engines/foundationdb/tests/status/separate_not_enough_servers.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_not_enough_servers` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=False, healthy=False, coordinators=coordinators=[address='127.0.0.1:4991', reachable=True], quorum_reachable=True, recovery_state=description='Recruiting new transaction servers.', name='recruiting_transaction_servers', required_logs=3, required_commit_proxies=1, required_grv_proxies=1, required_resolvers=1, data_state=healthy=True, name='healthy', processes=1, machines=1.
Configuration snapshot: coordinators_count=1, excluded_servers=[]. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
message names must remain stable: `cluster:unreadable_configuration`, `cluster:transaction_start_timeout`, `cluster:commit_timeout`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=False, healthy=False, quorum_reachable=True, messages=cluster:unreadable_configuration, cluster:transaction_start_timeout, cluster:commit_timeout, recovery=recruiting_transaction_servers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_not_enough_servers.json -->
