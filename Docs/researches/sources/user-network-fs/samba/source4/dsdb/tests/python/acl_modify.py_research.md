# sources/user-network-fs/samba/source4/dsdb/tests/python/acl_modify.py

## Purpose

`acl_modify.py` is a focused Samba AD DC LDAP ACL regression test for deleting `dNSHostName` from a computer account. It verifies that an ordinary authenticated user who can bind to LDAP cannot delete the `dNSHostName` attribute, whether the delete is submitted as a structured `Message` or as LDIF, and whether the delete specifies the old value or deletes all values.

This file overlaps conceptually with the broader `acl.py` DNS hostname modify tests but narrows the scenario to deletion denial.

## Important APIs, Types, and Helpers

- Command-line parsing mirrors other Samba Python tests: `SambaOptions`, `CredentialsOptions`, `SubunitOptions`, and `TestProgram` require one host argument and create `ldaphost`.
- Module globals `lp` and sealed `creds` are shared across tests.
- `AclTests.setUp()` opens an administrative `SamDB` with `system_session(lp)` and records `base_dn`.
- `AclTests.get_ldb_connection()` builds sealed non-Kerberos credentials for a named user and returns a user-bound `SamDB`.
- `AclModifyTests.setup_computer_with_hostname(account_name)` creates a temporary user, binds as that user, creates an OU and computer account as admin, sets the computer's `dNSHostName` as admin, registers cleanup for the user and OU tree, and returns `(host_name, dn)`.
- The four tests use `Message`, `MessageElement`, `Dn`, `FLAG_MOD_REPLACE`, `FLAG_MOD_DELETE`, and `modify_ldif()` to exercise both LDB object-message and LDIF code paths.
- Assertions use `assertRaisesLdbError(ERR_INSUFFICIENT_ACCESS_RIGHTS, ...)`.

## Control Flow

Each test derives an `account_name` from the test id and truncates it to 63 characters, then calls `setup_computer_with_hostname()`. The setup helper creates `OU=<account_name>,<base_dn>`, creates `CN=<account_name>` below it as a computer with `sAMAccountName=<account_name>$`, computes `<account_name>.<domain_dns_name>`, and writes that value to `dNSHostName` as admin.

The tests then attempt deletion as the ordinary user:

- `test_modify_delete_dns_host_name_specified()` sends a `MessageElement(host_name, FLAG_MOD_DELETE, 'dNSHostName')`.
- `test_modify_delete_dns_host_name_unspecified()` sends a `MessageElement([], FLAG_MOD_DELETE, 'dNSHostName')`.
- `test_modify_delete_dns_host_name_ldif_specified()` sends LDIF with `delete: dNSHostName` followed by the concrete hostname value.
- `test_modify_delete_dns_host_name_ldif_unspecified()` sends LDIF with `delete: dNSHostName` and no value.

All four are expected to fail with insufficient access rights.

## State and Persistence Behavior

The test mutates a live LDAP directory. For each test it creates a user named `mouse`, creates an OU named after the test method, creates one computer account, and writes `dNSHostName`. `addCleanup()` removes the user with `deleteuser` and deletes the OU using `tree_delete:0`, which should remove the computer below it. The module also creates a global admin `SamDB` named `ldb` at the bottom, though the tests primarily use `self.ldb_admin`.

Because `mouse` is reused in every test, concurrent execution against the same domain could collide. The OU/account names are derived from test ids and are more isolated.

## Dependencies and Integration Points

The file depends on Samba's Python runtime, an AD DC LDAP endpoint, LDB message APIs, and Samba test harness helpers. Its main integration point is the directory server ACL path that evaluates delete operations for `dNSHostName` on computer objects. It also indirectly depends on `SamDB.domain_dns_name()` to construct a valid hostname before attempting deletion.

## Risks and Maintenance Notes

- The helper imports `samba.dsdb` but does not use it; this is harmless but not necessary for the current tests.
- Like `acl.py`, URL host parsing uses `host.lstrip(start + 3)`, which is suspicious for URL input.
- Cleanup depends on `tree_delete:0`; if the server refuses tree delete or the connection fails, temporary OUs/computers can remain.
- The fixed user name `mouse` makes these tests unsuitable for parallel runs against a shared domain without additional isolation.
- The tests only assert the LDAP error code, not the diagnostic string, so they are robust to server message text changes but may miss more subtle diagnostic regressions.

## Test Signals

The strongest signal is that all four delete attempts consistently raise `ERR_INSUFFICIENT_ACCESS_RIGHTS`. Together they cover both specified-value and all-values deletion through both programmatic `modify()` and text `modify_ldif()` interfaces. A pass confirms that the deny behavior is enforced below the API surface and is not an artifact of only one client-side request representation.
