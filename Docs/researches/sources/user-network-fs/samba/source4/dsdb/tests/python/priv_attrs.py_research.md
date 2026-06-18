# sources/user-network-fs/samba/source4/dsdb/tests/python/priv_attrs.py

## Purpose

This executable Samba test suite validates protection around privileged AD object attributes even when generic create-child or write-property permissions are present. It focuses on attributes and `userAccountControl` flag combinations that can grant delegation, domain-controller-like behavior, SID history, Kerberos secondary TGT behavior, or privileged primary group membership. The goal is to ensure unprivileged users cannot set these values during add or modify operations, and that administrators also receive expected denials for attributes that are never valid to set directly in the tested context.

## Important APIs, Types, and Functions

The main test class is `PrivAttrsTests(samba.tests.TestCase)`, decorated with `@DynamicTestCase`. The global `attrs` table is the key test data structure. Each entry describes the LDAP attribute or logical test case, the value to apply, and expected privileged or unprivileged errors. Some logical entries map to `userAccountControl` with flag combinations:

- `UF_TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION`
- `UF_TRUSTED_FOR_DELEGATION`
- `UF_SERVER_TRUST_ACCOUNT`
- `UF_PARTIAL_SECRETS_ACCOUNT`
- `UF_WORKSTATION_TRUST_ACCOUNT`
- `UF_NORMAL_ACCOUNT`
- `UF_PASSWD_NOTREQD`

Other protected attributes include `sidHistory`, `msDS-AllowedToDelegateTo`, `msDS-SecondaryKrbTgtNumber`, and `primaryGroupID`.

Important methods:

- `get_creds()` constructs sealed, non-Kerberos credentials for the unprivileged test user.
- `assertGotLdbError()` enforces exact error codes when `STRICT_CHECKING=1`, or only non-success when strict checking is disabled.
- `setUp()` creates an OU, creates an unprivileged user, gathers SIDs, opens admin and unprivileged `SamDB` connections, and prepares `SDUtils`.
- `setUpDynamicTestCases()` generates the Cartesian product of attribute scenario, operation mode, permission mode, security descriptor mode, and object class.
- `add_computer_ldap()`, `add_user_ldap()`, and `add_thing_ldap()` build and add test objects.
- `_test_priv_attr_with_args()` contains the generated test implementation.

## Control Flow

At startup, the script parses a target host, normalizes it to `ldaphost`, obtains sealed credentials, and runs the generated test suite through `SubunitTestRunner`.

For each dynamic case, `_test_priv_attr_with_args()`:

1. Resolves the real LDAP attribute name and whether the protected value should be present during add or later modification.
2. Chooses either the admin connection or unprivileged connection. For unprivileged create-child testing, it grants object-specific `CC` ACEs for user and computer classes on the test OU.
3. Optionally includes an `ntSecurityDescriptor` on the new object that grants the unprivileged user read/write property and change-password rights, simulating an admin-created object with broad write-property access.
4. Runs add-time checks, including Windows compatibility filters for object-class-only cases (`only-1`, `only-2`) and expected admin denials (`priv-error`).
5. For modify cases, first creates a baseline object and then attempts either delete/add or replace against the protected attribute as the unprivileged user.
6. Verifies that the resulting LDAP error matches the scenario's expected denial.

## State and Persistence Behavior

Each test creates and deletes a dedicated OU under the domain naming context: `OU=test_priv_attrs,<base_dn>`. It then creates an unprivileged user inside that OU and may create additional user or computer objects named `privattrs`. Security descriptors on the OU and newly created objects are modified to grant controlled permissions. `delete_force(..., controls=["tree_delete:0"])` removes the OU at setup time and cleanup handlers remove the unprivileged user.

The generated tests repeatedly mutate DACLs on the test OU and create objects in the same OU. Because setup recreates the OU per test case, the intended persistence scope is one generated test method.

## Dependencies and Integration Points

The file uses Samba command-line option parsing, `SamDB` LDAP operations, `samba.tests.DynamicTestCase`, `SubunitTestRunner`, `sd_utils.SDUtils`, NDR packing of security descriptors and SIDs, and LDAP constants from `ldb`. It integrates with AD security descriptor syntax through SDDL strings and object-specific ACE GUIDs for user/computer create-child permissions. It intentionally disables Kerberos for the unprivileged account because repeated `kinit` use is too expensive in this dynamic matrix.

## Risks and Edge Cases

The generated matrix is broad and expensive: `len(attrs) * 3 operation modes * 2 permission modes * 2 SD modes * 2 object classes`. Its correctness depends on the `attrs` metadata matching AD behavior. `STRICT_CHECKING=0` weakens exact-code assertions and can hide compatibility drift by accepting any failure. Some entries encode Windows behavior quirks with `only-1` and `only-2`, so a new directory implementation may need explicit review before changing those expectations.

The test intentionally grants powerful-looking write permissions and create rights. The core risk under test is that generic ACL success must not override attribute-specific privilege checks for delegation, DC/RODC account flags, SID history, or primary group elevation.

## Test Signals

A passing run means unprivileged users cannot set protected attributes during add, delete/add modify, or replace modify, even with create-child rights or write-property ACEs. It also signals that privileged/admin attempts fail where Samba expects schema or system-only restrictions. Failures identify either an authorization bypass, an object-class validation mismatch, or a changed LDAP error-code contract.
