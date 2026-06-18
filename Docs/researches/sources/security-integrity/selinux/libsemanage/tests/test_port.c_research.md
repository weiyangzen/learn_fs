# sources/security-integrity/selinux/libsemanage/tests/test_port.c

## Purpose
`test_port.c` validates libsemanage port-context records, including protocol/range/context record operations, compiled-policy queries, local-store CRUD, and an internal local validation path for port customizations.

## Important APIs, Types, and Functions
The suite targets `semanage_port_t` and `semanage_port_key_t`. Record functions covered include `semanage_port_create`, `semanage_port_key_create`, `semanage_port_key_extract`, `semanage_port_compare`, `semanage_port_compare2`, `semanage_port_set_proto`, `semanage_port_get_proto`, `semanage_port_get_proto_str`, `semanage_port_set_port`, `semanage_port_set_range`, `semanage_port_get_low`, `semanage_port_get_high`, `semanage_port_set_con`, `semanage_port_get_con`, and `semanage_port_clone`.

Policy APIs covered are `semanage_port_query`, `semanage_port_exists`, `semanage_port_count`, `semanage_port_iterate`, and `semanage_port_list`. Local APIs covered are `semanage_port_modify_local`, `semanage_port_del_local`, `semanage_port_query_local`, `semanage_port_exists_local`, `semanage_port_count_local`, `semanage_port_iterate_local`, and `semanage_port_list_local`. The final internal validation group drives commit-time validation through `helper_commit`.

## Control Flow
`port_test_init` creates the direct test store and loads `test_port.policy`; cleanup destroys the store. `port_add_tests` registers record, policy, local, and validation tests. The helper layer fetches nth ports and keys from `semanage_port_list` and provides local add/delete wrappers.

The record tests compare same and different keys/records, check protocol string mapping for invalid and known values, verify range setters, create a default record, and clone a populated record. Policy tests read the compiled policy and compare low/high/protocol/context values. Local tests stage records in a transaction, query before and after deletion, and verify local counts, iteration, and lists. `test_port_validate_local` runs three commit scenarios: deleting an existing local port, committing one local port, and committing two adjacent UDP ranges with different contexts.

## State and Persistence Behavior
The suite persists local port changes through the libsemanage transaction system under `test-policy`. Some tests explicitly commit and then reopen transactions to force file-backed validation. Local validation tests depend on commit side effects and clean up by reopening a transaction and deleting local records.

## Dependencies and Integration Points
Dependencies include CUnit, shared `utilities.h`, libsemanage port/context APIs, libsepol protocol constants, and the `test_port.policy` fixture. The suite is exposed through `port_test_init`, `port_test_cleanup`, and `port_add_tests`.

## Risks and Edge Cases
Static iterate counters are not reset per repeated suite execution. Protocol numeric assumptions are embedded directly: `0` maps to UDP, `1` to TCP, `2` to DCCP, and `3` to SCTP. Some validation helpers delete records during cleanup that may already have been removed, relying on the current local-store behavior and assertion placement. The fixture order must remain stable for nth-record selection.

## Test Signals
Signals include `PORT_COUNT == 3`, correct protocol labels including `"???"` for unknown values, context equality after set/clone/query, local count transitions from 0 to 2 and back to 0, iteration/list counts of 3, and successful commit of local validation scenarios.
