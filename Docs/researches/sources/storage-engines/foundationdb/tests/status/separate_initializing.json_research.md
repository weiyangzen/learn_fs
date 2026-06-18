<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_initializing.json -->
# sources/storage-engines/foundationdb/tests/status/separate_initializing.json

## Purpose
Golden FoundationDB status JSON fixture for the `separate_initializing` scenario. It captures expected client/cluster status shape, health, coordinator reachability, messages, recovery state, process inventory, and workload counters for status parser/formatter tests.

## Important APIs, Types, And Functions
The fixture uses the status JSON schema with top-level keys `client`, `cluster`. Client fields include `cluster_file`, `coordinators`, `database_status`, `messages`, `timestamp`; cluster fields include `cluster_controller_timestamp`, `configuration`, `data`, `latency_probe`, `machines`, `messages`, `processes`, `qos`, `recovery_state`, `workload`.

## Control Flow
No executable control flow lives in this file. Test code loads the JSON, traverses client and cluster sections, and verifies that status interpretation handles reachable/unreachable coordinators, missing cluster sections, health flags, and message arrays.

## State And Persistence Behavior
Captured state: database_status=available=True, healthy=True, coordinators=coordinators=[address='127.0.0.1:4991', reachable=True], quorum_reachable=True, recovery_state=description='Recovery complete.', name='fully_recovered', data_state=description='(Re)initializing automatic data distribution.', name='initializing', processes=1, machines=1.
Configuration snapshot: coordinators_count=1, excluded_servers=[], redundancy=factor='single', storage_engine='memory'. Fault tolerance snapshot: absent.

## Dependencies And Integration Points
Integrated with FoundationDB status tests and expected text fixtures in the same folder. It depends on the status JSON contract produced by `fdbcli status json`/status clients and on parser code preserving message names and health fields.

## Risks
data state carries scenario-specific health semantics

## Test Signals
Expected signals include availability=True, healthy=True, quorum_reachable=True, messages=none, recovery=fully_recovered.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/tests/status/separate_initializing.json -->
