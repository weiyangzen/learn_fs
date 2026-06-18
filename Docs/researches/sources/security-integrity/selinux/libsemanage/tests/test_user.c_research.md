# sources/security-integrity/selinux/libsemanage/tests/test_user.c

## Purpose
`test_user.c` validates libsemanage SELinux user-record behavior, including record fields, role list mutation, compiled-policy queries, and local-store CRUD.

## Important APIs, Types, and Functions
The suite targets `semanage_user_t` and `semanage_user_key_t`. It exercises `semanage_user_create`, `semanage_user_free`, `semanage_user_key_create`, `semanage_user_key_extract`, `semanage_user_compare`, `semanage_user_compare2`, `semanage_user_set_name`, `semanage_user_get_name`, `semanage_user_set_prefix`, `semanage_user_get_prefix`, `semanage_user_set_mlslevel`, `semanage_user_get_mlslevel`, `semanage_user_set_mlsrange`, `semanage_user_get_mlsrange`, `semanage_user_get_num_roles`, `semanage_user_add_role`, `semanage_user_del_role`, `semanage_user_has_role`, `semanage_user_get_roles`, `semanage_user_set_roles`, and `semanage_user_clone`.

Policy APIs covered are `semanage_user_query`, `semanage_user_exists`, `semanage_user_count`, `semanage_user_iterate`, and `semanage_user_list`. Local APIs covered are `semanage_user_modify_local`, `semanage_user_del_local`, `semanage_user_query_local`, `semanage_user_exists_local`, `semanage_user_count_local`, `semanage_user_iterate_local`, and `semanage_user_list_local`.

## Control Flow
`user_test_init` creates a test store and loads `test_user.policy`; cleanup destroys the store. `user_add_tests` registers record, policy, and local cases. Helpers fetch nth users and keys from `semanage_user_list`, then use those fixtures to add and delete local records.

Record tests validate scalar fields and role-list APIs. Query/list tests verify the compiled policy exposes three users and returns non-null records. Local tests add policy users to the local store, commit and reopen for query/delete persistence, and verify existence, count, iteration, and list behavior.

## State and Persistence Behavior
The suite stores temporary policy data under `test-policy`. Local user modifications are staged in transactions and persisted on `helper_commit`; `test_user_modify_del_query_local` explicitly checks query behavior after commit. Role arrays returned by `semanage_user_get_roles` are freed by the test after use.

## Dependencies and Integration Points
Dependencies include CUnit, shared `utilities.h`, libsemanage user APIs, and `test_user.policy`. Integration with the runner is through `user_test_init`, `user_test_cleanup`, and `user_add_tests`.

## Risks and Edge Cases
Several policy query/list assertions are shallow and include TODO comments for checking real field values. `test_user_clone` appears to assert fields on the original record after cloning rather than on `user_clone`, so it only verifies the clone call returned success and not clone content. `test_user_exists_local` declares an unused `user` pointer and frees it as NULL. Static iterate counters are not reset between repeated invocations.

## Test Signals
Primary signals are `USER_COUNT == 3`, successful setter/getter round trips for name/prefix/MLS level/range, role-list add/set/delete behavior, non-null query/list records, local existence/count/list/iterate results, and negative query after local deletion.
