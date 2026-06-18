<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_no_servers.json -->
# sources/storage-engines/foundationdb/tests/status/separate_no_servers.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_no_servers` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include none for controller-unreachable cases.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=False, healthy=False, coordinators=coordinators=[address='127.0.0.1:4991', reachable=True], quorum_reachable=True, recovery_state=absent, data_state=absent, processes=0, machines=0.
Configuration snapshot: absent. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
cluster section is intentionally absent, so consumers must tolerate partial status documents; message names must remain stable: `client:no_cluster_controller`; fixture represents unhealthy/unavailable state and should not be normalized as success

## Test Signals
Expected signals include availability=False, healthy=False, quorum_reachable=True, messages=client:no_cluster_controller, recovery=absent.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_no_servers.json -->
