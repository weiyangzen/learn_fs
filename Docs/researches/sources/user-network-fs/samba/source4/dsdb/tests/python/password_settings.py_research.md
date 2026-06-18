# sources/user-network-fs/samba/source4/dsdb/tests/python/password_settings.py

## Purpose

`password_settings.py` tests AD Password Settings Objects (PSOs), resultant PSO calculation, and related domain password policy behavior. It covers PSO precedence, direct versus group application, nested groups, equal-precedence GUID tie-breaking, invalid PSO locations, min/max password age, built-in and primary groups, permissions, user-add behavior, complexity, minimum length, and password history.

## Important APIs, Types, and Functions

- `PasswordSettingsTestCase` extends `PasswordTestCase`.
- `setUp()` connects to `SERVER_IP`, creates a temporary OU, allows password changes, snapshots domain defaults as `PasswordSettings(None, self.ldb)`, and tracks external objects for cleanup.
- `add_group()`, `add_user()`, `set_attribute()`, and `add_obj_cleanup()` are local object-management helpers.
- `assert_password_invalid()` and `assert_password_valid()` validate password set outcomes and expected `0000052D` policy errors.
- `assert_PSO_applied()` checks `msDS-ResultantPSO` and then verifies complexity, minimum length, and history enforcement for that PSO.
- `PSO_with_lowest_GUID()` implements equal-precedence tie expectation by fetching and sorting `objectGUID`.
- `get_ldb_connection()` creates a sealed LDAP connection as a regular test user for permissions checks.
- `format_password_for_ldif()` encodes quoted UTF-16LE `unicodePwd` values.

## Control Flow

Basic PSO tests create several PSOs with different precedence and password policy values, apply them to groups and users, then move group memberships and direct applies to prove the expected resultant PSO wins. Nested-group tests build membership chains and verify PSOs flow through nested groups; changing precedence and deleting PSOs must change the result. Equal-precedence tests apply PSOs with identical precedence and expect the lowest GUID to win, first through group membership and then through direct user application.

Invalid-location tests prove PSOs and Password Settings Containers cannot be created under an OU, and that a PSO placed under an invalid container outside the official Password Settings Container has no effect even if applied. Min-age tests sleep until `password_age_min` expires. Max-age tests compare `msDS-UserPasswordExpiryTimeComputed` against domain expiry using one-day deltas.

Special-group tests apply PSOs to `Domain Users`, `Domain Guests`, `Domain Admins`, and builtin groups, checking builtin groups are excluded while primary-group and nested-domain-group membership can influence resultant PSO. None-applied tests verify non-users, non-normal accounts, and `krbtgt` do not expose a resultant PSO. Permissions tests bind as an ordinary user and verify PSO creation, modification, and attribute reads are denied while admin operations succeed.

The add-user test demonstrates that a Domain Users PSO does not apply during a one-step LDAP add with `unicodePwd`, but does apply once the user exists and the password is modified. Domain history tests directly change `pwdHistoryLength` and confirm history enforcement, including transitions from zero to nonzero.

## State and Persistence Behavior

The suite creates a temporary OU and deletes it with `tree_delete:1`. PSOs and invalid containers live outside the OU, so their DNs are tracked in `test_objs` and deleted in `tearDown()`. Some tests modify domain `pwdHistoryLength`, but register cleanup to restore it. User password history and resultant PSO are real directory state, so helper `TestUser` mirrors old password lists to know which values should be valid after history length changes.

## Dependencies and Integration Points

The file depends on `samba.tests.pso.PasswordSettings`, `TestUser`, `PasswordTestCase`, `connect_samdb`, `create_test_ou`, `env_get_var_value("SERVER_IP")`, LDB modify flags, `samba.dsdb`, credentials/GENSEC sealing, and `unicodePwd` encoding. It integrates DSDB resultant-PSO computation, group expansion, primary group handling, schema superior rules, ACLs for PSO objects, password policy enforcement, generated expiry-time computation, and domain password-history attributes.

## Risks and Edge Cases

- Tests that sleep for min-age can flap if time resolution or scheduling is poor.
- GUID tie-breaking assumes byte-sort behavior from `objectGUID` values.
- Builtin group exclusion and primary-group inclusion are subtle and easy to regress in group expansion code.
- Permissions checks rely on default ACLs for the Password Settings Container.
- One-step user-add behavior intentionally mirrors Windows even though it may appear counterintuitive.
- Cleanup must remove PSOs outside the OU and restore `pwdHistoryLength`.

## Test Signals

Signals include exact `msDS-ResultantPSO` DN, accepted/rejected passwords for complexity, length, age, and history, PSO precedence changes after membership/preference changes, lowest-GUID tie-breaking, invalid-container no-op behavior, ordinary-user access denials, expected user-add policy behavior, and domain history enforcement when `pwdHistoryLength` changes.
