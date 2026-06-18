# sources/user-network-fs/samba/source4/dsdb/tests/python/unicodepwd_encrypted.py

## Purpose

`unicodepwd_encrypted.py` is an LDAP integration test for Samba AD password-change transport requirements. It verifies that writes to the sensitive `unicodePwd` attribute are accepted only when the LDAP connection is protected by SASL sealing or TLS, and rejected on unsigned or merely signed plaintext LDAP sessions.

## Important APIs, Types, and Functions

`UnicodePwdEncryptedConnectionTests` inherits from `PasswordTestCase`, using `allow_password_changes()` to relax policy during the test. `setUp()` creates a sealed `SamDB` connection, creates `cn=testuser,cn=users,<domain>`, sets an initial `userPassword`, and enables the account. `modify_unicode_pwd()` performs the actual `FLAG_MOD_REPLACE` on `unicodePwd`, encoding the quoted password as UTF-16LE as required by Active Directory semantics. The test methods cover SASL-sealed LDAP, SASL without seal, simple bind over plain LDAP, and simple bind over LDAPS.

## Control Flow

Command-line parsing builds Samba loadparm and credentials, then `TestProgram` runs the test class. Each test starts from a clean test user. The success paths call `modify_unicode_pwd()` directly. The rejection paths create alternate `SamDB` connections: one with `gensec.FEATURE_SEAL` removed and `client ldap sasl wrapping` forced to `sign`, and another using simple bind over `ldap://`. Both expect `LdbError` with `ERR_UNWILLING_TO_PERFORM` and a diagnostic saying password modification must be over an encrypted connection.

## State and Persistence Behavior

The test mutates live directory state by deleting and recreating `testuser`, setting `userPassword`, enabling the account, and replacing `unicodePwd`. It intentionally touches password-change policy through `allow_password_changes()`. Cleanup relies on per-test recreation through `delete_force`; the tested password value is not reused outside the current test case.

## Dependencies and Integration Points

The file depends on Samba Python bindings for `SamDB`, `system_session`, credentials and GENSEC feature flags, plus LDB message APIs. It exercises the DSDB password modification path reached through LDAP server connections, not a mocked password module. It also depends on an LDAPS listener being available for the TLS simple-bind positive case.

## Risks and Edge Cases

The no-seal SASL case requires Kerberos-required credentials or the client may negotiate a protected connection automatically, so the test explicitly masks seal and forces signing. Simple bind setup uses `get_admin_sid()` as the bind DN, which makes the test sensitive to Samba's simple-bind credential interpretation. Failures can come from TLS/listener setup rather than password policy if LDAPS is unavailable.

## Test Signals

Strong signals are: sealed SASL and LDAPS simple bind successfully replace `unicodePwd`; unsealed LDAP and plain simple bind fail with `ERR_UNWILLING_TO_PERFORM`; and the error text identifies the encrypted-connection requirement.
