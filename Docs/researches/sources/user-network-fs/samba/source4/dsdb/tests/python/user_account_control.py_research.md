# sources/user-network-fs/samba/source4/dsdb/tests/python/user_account_control.py

## Purpose

`user_account_control.py` is a large Samba AD integration suite for non-ACL rules around `userAccountControl`, objectClass compatibility, machine-account creation rights, privileged trust-account transitions, trailing-dollar rules, and `primaryGroupID` restrictions. It checks behavior for both domain-admin and delegated/unprivileged writers.

## Important APIs, Types, and Functions

`UserAccountControlTests` is decorated with `DynamicTestCase` and generates many parameterized tests in `setUpDynamicTestCases()`. Helpers include `add_computer_ldap()`, `add_user_ldap()`, and `get_creds()`. `setUp()` creates an unprivileged user, a test OU, SAMR connection, security descriptor utilities, and reference computer security descriptors. Major test helpers include `_test_uac_bits_set_with_args()`, `_test_uac_bits_unrelated_modify_with_args()`, `_test_uac_bits_add_with_args()`, `_test_objectclass_uac_dollar_lock_with_args()`, `_test_mod_lock_with_args()`, `_test_objectclass_uac_mod_lock_with_args()`, and `_test_objectclass_mod_lock_with_args()`.

## Control Flow

The suite first establishes a controlled OU and grants temporary object creation or write-property ACEs to the unprivileged principal. Individual tests then add users or computers and attempt UAC, objectClass, `sAMAccountName`, security descriptor, and primary group changes. Expected results distinguish successful normal-account operations from `ERR_INSUFFICIENT_ACCESS_RIGHTS`, `ERR_OBJECT_CLASS_VIOLATION`, `ERR_UNWILLING_TO_PERFORM`, and `ERR_OTHER`. Dynamic cases cover transitions among `UF_NORMAL_ACCOUNT`, `UF_WORKSTATION_TRUST_ACCOUNT`, `UF_SERVER_TRUST_ACCOUNT`, and invalid or privileged bits using replace and delete-add modify styles.

## State and Persistence Behavior

Every test mutates a live AD database. `setUp()` removes and recreates the OU and unprivileged user, then registers cleanup for the user and OU tree. The suite temporarily changes OU DACLs and sometimes object DACLs to isolate semantic restrictions from ordinary ACL denial. It also modifies group membership and `primaryGroupID` for test accounts. No durable state is intended beyond the test run, but failed teardown can leave generated accounts under the test OU.

## Dependencies and Integration Points

The tests exercise DSDB object creation, SAMR connectivity, security descriptor packing/unpacking, extended rights for creating computer objects, UAC validation in the objectclass/user module stack, and primary group validation. They rely on `samba.dsdb` UAC constants, `security` RID/SID values, `sd_utils`, LDB search/modify APIs, sealed LDAP credentials, and a live DC accepting both LDAP and SAMR connections.

## Risks and Edge Cases

The test intentionally grants broad write-property ACEs in some scenarios, so it must run only against disposable test domains. Error expectations encode Samba/Windows compatibility decisions and may need updates when DSDB validation ordering changes. Some generated test names include `None` string fragments from optional parameter combinations, which is harmless but easy to misread. The suite is expensive because it creates many dynamic tests and uses live LDAP/SAMR setup per case.

## Test Signals

Important signals include blocked unprivileged promotion to DC/RODC/trust accounts, objectClass/UAC mismatch failures, ignored or invalid UAC bits not sticking, allowed admin transitions where appropriate, protection against setting privileged `primaryGroupID` on create, and prohibition on changing structural objectClass after creation.
