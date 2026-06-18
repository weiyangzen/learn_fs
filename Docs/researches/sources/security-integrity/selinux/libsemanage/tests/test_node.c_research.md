# sources/security-integrity/selinux/libsemanage/tests/test_node.c

## Purpose
`test_node.c` validates libsemanage node-context record handling for IPv4 and IPv6 network nodes, including record creation, key extraction, address and mask setters, protocol handling, compiled-policy queries, and local-store mutation.

## Important APIs, Types, and Functions
The suite exercises `semanage_node_t` and `semanage_node_key_t`. Record-level coverage includes `semanage_node_create`, `semanage_node_key_create`, `semanage_node_key_extract`, `semanage_node_compare`, `semanage_node_compare2`, `semanage_node_set_addr`, `semanage_node_get_addr`, `semanage_node_set_addr_bytes`, `semanage_node_get_addr_bytes`, `semanage_node_set_mask`, `semanage_node_get_mask`, `semanage_node_set_mask_bytes`, `semanage_node_get_mask_bytes`, `semanage_node_set_proto`, `semanage_node_get_proto`, `semanage_node_get_proto_str`, `semanage_node_set_con`, `semanage_node_get_con`, and `semanage_node_clone`.

Policy APIs covered are `semanage_node_query`, `semanage_node_exists`, `semanage_node_count`, `semanage_node_iterate`, and `semanage_node_list`. Local APIs covered are `semanage_node_modify_local`, `semanage_node_del_local`, `semanage_node_query_local`, `semanage_node_exists_local`, `semanage_node_count_local`, `semanage_node_iterate_local`, and `semanage_node_list_local`.

## Control Flow
`node_test_init` creates the direct test policy store and loads `test_node.policy`; `node_test_cleanup` destroys that store. `node_add_tests` registers record, policy, and local cases. Helper functions fetch nth records and keys from `semanage_node_list` and use them to seed local-store operations.

The record tests cover both textual and byte-vector address/mask paths. Policy tests query and compare address, mask, protocol, and context data from the compiled policy. Local tests run in transactions, write policy records into the local store, commit where persistence needs to be checked, then verify query, existence, count, iteration, listing, and deletion.

## State and Persistence Behavior
The suite creates and removes `test-policy` via shared utilities. Local node customizations are staged inside libsemanage transactions; `test_node_modify_del_query_local` commits, reopens a transaction, and verifies that local query sees the persisted record. It also adds a temporary second record with a modified IPv4 address to exercise qsort comparison paths for local node serialization.

## Dependencies and Integration Points
Dependencies include CUnit, the shared `utilities.h` handle/store helpers, libsemanage and libsepol protocol constants, and the binary fixture `test_node.policy`. It integrates with the runner through `node_test_init`, `node_test_cleanup`, and `node_add_tests`.

## Risks and Edge Cases
The byte-array tests use `char` values such as 192 and 255, which may be signed on some targets; the test compares byte-for-byte through the same representation and is mainly a round-trip check. Static iterate counters are not reset per invocation. As with other record suites, nth-record selection depends on deterministic list ordering from the fixture policy.

## Test Signals
Expected signals are successful CUnit assertions that protocol strings are `"ipv4"` and `"ipv6"`, text and byte setters round-trip, cloned nodes preserve address/mask/protocol/context, policy count equals `NODE_COUNT`, and local add/delete/count/list operations behave consistently across transactions.
