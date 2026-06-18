# sources/user-network-fs/samba/source4/dsdb/tests/python/passwords.py

## Purpose

This file is an executable Samba AD DS password-behavior test suite. It validates LDAP password set and change semantics for AD-style password attributes (`unicodePwd`, `userPassword`, `clearTextPassword`, `dBCSPwd`), password history and previous-password simple bind behavior, `dSHeuristics`-controlled `userPassword` handling, policy hint controls, Protected Users handling, empty-value rejection, and edge-case LDIF operation ordering. It is designed to run against Samba and, for many cases, Windows Server when the LDAP connection is sufficiently protected.

The script parses Samba loadparm, credentials, subunit, and host options at import time, forces gensec sealing on command-line credentials, normalizes the host to LDAP/LDAPS/TDB URLs near the bottom, and invokes `TestProgram(module=__name__, opts=subunitopts)`.

## Important APIs, Types, and Functions

The main type is `PasswordTests(PasswordTestCase)`. It inherits shared password-policy helpers from `samba.tests.password_test.PasswordTestCase`, including `allow_password_changes()`. Setup opens an administrative `SamDB` connection as `self.ldb`, creates `cn=testuser,cn=users,<domain>`, establishes an initial password through special `userPassword` delete/add LDIF syntax, enables the account, then opens `self.ldb2` as that user with sealed credentials.

Key helpers:

- `_upwd_encode(password)` wraps a password in double quotes, UTF-16LE encodes it, and base64 encodes the result for `unicodePwd` LDIF.
- `_replace_unicode_pwd(ldb, old=None, new=None, controls=None)` constructs either password-change LDIF (`delete` old then `add` new) or password-reset LDIF (`replace`) against `unicodePwd`, optionally with LDAP controls.
- `_set_pwd_properties()` repeatedly writes `pwdProperties` and polls for convergence to handle Windows timing races.
- `_set_pwd_property_bits()` toggles password-property bits, mainly `DOMAIN_PASSWORD_COMPLEX`.
- `_test_unicodePwd_policy_hints_history()`, `_test_unicodePwd_policy_hints_complexity()`, `_test_unicodePwd_policy_hints_length()`, and `_test_unicodePwd_policy_hints_password_age()` centralize policy-hints behavior across the modern and deprecated control OIDs.

Important test methods cover:

- Hash-based `unicodePwd` and `dBCSPwd` set/change rejection.
- Cleartext `unicodePwd`, `userPassword`, and Samba-only `clearTextPassword` set/change paths.
- Immediate previous password simple-bind acceptance, older password rejection, and history-based reuse rejection, including rename/salt-change cases.
- Protected Users group membership combined with `unicodePwd` set/change.
- Admin reset behavior under policy hints for history, complexity, length, and password age.
- Invalid LDIF shapes and operation ordering in `test_failures()`.
- Empty attribute value handling in `test_empty_passwords()`.
- Plain LDAP `userPassword` attribute storage/readback when `dSHeuristics` disables password-change interpretation.
- Connection-local `dSHeuristics` behavior in `test_modify_dsheuristics_userPassword()`.
- Zero-length password allowance when `minPwdLength` and complexity properties are temporarily relaxed.

## Control Flow

The suite starts by proving invalid initial password-change syntax fails before using a special admin-style `userPassword` delete/add without an old value to set the first password. This setup creates a clean, enabled account and a second bind as the test user. Each test then mutates password-related attributes through `SamDB.modify()`, `modify_ldif()`, `setpassword()`, account group membership changes, or direct domain policy writes.

The control flow is mostly assertion-driven:

- Set/reset tests build `ldb.Message` instances or LDIF strings and call administrative `self.ldb`.
- User-change tests call `self.ldb2` so access checks and old-password validation run as the account itself.
- Expected failures catch `LdbError`, compare the LDAP error code, and sometimes inspect Windows/Samba diagnostic substatus strings such as `00000056`, `0000052D`, `HRES_SEC_E_INVALID_TOKEN`, or `WERR_PASSWORD_RESTRICTION`.
- Policy-hints tests intentionally change domain policy attributes, register cleanup handlers, and then exercise user changes and admin resets with and without controls.
- Teardown removes `testuser` and `testuser2` and drops the secondary connection reference.

## State and Persistence Behavior

The file directly changes persistent directory state in a live AD database: user objects, passwords, group membership, domain password policy attributes (`pwdProperties`, `minPwdLength`, min/max password age), and `dSHeuristics`. It uses `delete_force()` to clean test users in setup and teardown and uses `addCleanup()` for selected policy restoration paths. Some tests deliberately sleep after `dSHeuristics` or policy writes because behavior may be cached per connection or asynchronously visible, especially against Windows.

Password history and old-password acceptance are central stateful behaviors. The tests assume domain `pwdHistoryLength` is high enough for some history assertions, branch for FL2003-like low-history behavior in policy-hint checks, and verify that renaming an account does not invalidate previous-password history semantics.

## Dependencies and Integration Points

The script integrates with Samba's Python test runner (`samba.tests.subunitrun.TestProgram`), credentials/loadparm option handling, `SamDB`, `ldb.Message` and LDIF modification APIs, domain policy helper methods on `SamDB`, and constants from `samba.dcerpc.security`, `samba.dcerpc.samr`, `samba.hresult`, `samba.werror`, and `ldb`. It depends on encrypted LDAP or LDAPS for password operations and creates both administrative and end-user LDAP sessions.

Integration with Windows compatibility is explicit: comments and assertions allow Windows-specific `ERR_NO_SUCH_ATTRIBUTE` for `clearTextPassword`, mention required `dSHeuristics` settings for `userPassword`, and note races in domain policy propagation.

## Risks and Edge Cases

The suite is intentionally invasive: it changes domain policy and `dSHeuristics`, so cleanup correctness is important. Several paths restore state manually after a successful sequence rather than via `finally`, so an unexpected exception can leave policy changes behind until broader test cleanup or environment reset. Timing sleeps are coarse and can be flaky on slow replication/caching paths. `host_ldaps` is `None` for TDB/non-LDAP hosts, but old-password simple bind tests assume LDAPS is usable; these are effectively LDAP-server tests.

Security-sensitive risk areas are well covered: direct hash writes must remain rejected, empty values must not bypass password handling, malformed multi-operation LDIF must not produce partial unintended state, ordinary users must not reset their own passwords through replace operations, and `dSHeuristics` must not accidentally expose password material on existing connections.

## Test Signals

Successful execution signals that Samba's password modules enforce AD-compatible password set/change contracts, old-password grace and history behavior, LDAP error mapping, policy hints, and `userPassword` handling. Failure signals often identify a regression in password ACL routing, policy enforcement, protected-user support, `dSHeuristics` caching, or compatibility with Windows diagnostic codes. The suite's own assertions are the primary test signal; it does not include separate unit mocks or fixture files.
