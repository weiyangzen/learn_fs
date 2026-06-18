# sources/security-integrity/selinux/libsemanage/tests/test_iface.c

## Purpose
`test_iface.c` is a CUnit suite for the libsemanage interface-record API and the policy/local backend wrappers for network interfaces. It verifies that interface records can be created, keyed, cloned, compared, read from compiled policy, and written/deleted through the local customization store.

## Important APIs, Types, and Functions
The suite exercises `semanage_iface_t` and `semanage_iface_key_t` plus the `semanage_iface_*` API family. Public record functions covered include `semanage_iface_create`, `semanage_iface_free`, `semanage_iface_key_create`, `semanage_iface_key_extract`, `semanage_iface_compare`, `semanage_iface_compare2`, `semanage_iface_get_name`, `semanage_iface_set_name`, `semanage_iface_get_ifcon`, `semanage_iface_set_ifcon`, `semanage_iface_get_msgcon`, `semanage_iface_set_msgcon`, and `semanage_iface_clone`. Policy-store functions covered include `semanage_iface_query`, `semanage_iface_exists`, `semanage_iface_count`, `semanage_iface_iterate`, and `semanage_iface_list`. Local-store functions covered include `semanage_iface_modify_local`, `semanage_iface_del_local`, `semanage_iface_query_local`, `semanage_iface_exists_local`, `semanage_iface_count_local`, `semanage_iface_iterate_local`, and `semanage_iface_list_local`.

The file defines three expected interface fixtures: `eth0`, `eth1`, and `eth2`, with matching interface and packet/message contexts. Helper functions `get_iface_nth`, `get_iface_key_nth`, `add_local_iface`, and `delete_local_iface` centralize list extraction and local-store mutation.

## Control Flow
`iface_test_init` creates a temporary direct policy store through `create_test_store` and loads `test_iface.policy` as `policy.kern`. `iface_add_tests` registers record, policy, and local tests into a supplied CUnit suite. Most tests call `setup_handle(SH_CONNECT)` to connect to the test store or `setup_handle(SH_TRANS)` to open a transaction, perform assertions, then call `cleanup_handle` at the same level.

Record tests operate on policy records fetched through `semanage_iface_list`. Query/existence/count/list/iterate tests read from the active policy view. Local tests start a transaction, copy policy records into the local customization layer, sometimes commit and reopen the transaction to force persistence to disk, then query, count, iterate, list, and delete those local records.

## State and Persistence Behavior
The test store lives under `test-policy` and is destroyed by `iface_test_cleanup`. Local interface changes are transaction-scoped until `helper_commit`; `test_iface_modify_del_query_local` explicitly commits and begins a new transaction before verifying `semanage_iface_query_local`, so it checks serialized local-file behavior rather than only in-memory mutation. Helpers free all unselected list records to avoid leaking list results.

## Dependencies and Integration Points
The suite depends on CUnit, `utilities.h` test-store helpers, libsemanage public headers, and the binary fixture `test_iface.policy`. It integrates with the larger libsemanage test runner through `iface_test_init`, `iface_test_cleanup`, and `iface_add_tests`.

## Risks and Edge Cases
The iterate counters are static globals and are not reset inside each test, so repeated invocation in a single process could produce false failures. Test registration has two typo-like display names, `"iface_create)"` and `"iface_clone);"`, which do not affect function execution but can confuse reports. The suite assumes policy list ordering is stable enough for `I_FIRST`, `I_SECOND`, and `I_THIRD` to identify the fixture records.

## Test Signals
Primary signals are CUnit assertions that policy count equals `IFACE_COUNT`, compare functions distinguish equal and non-equal keys/records, context setters round-trip through `CU_ASSERT_CONTEXT_EQUAL`, policy queries match expected records, and local mutations survive commit and deletion.
