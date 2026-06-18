# sources/user-network-fs/samba/source4/dsdb/tests/python/login_basics.py

## Purpose

`login_basics.py` sanity-checks that a normal AD user can authenticate over Kerberos, NTLM, and LDAPS simple bind, that bad passwords update bad-password state, and that password changes through `userPassword` affect subsequent authentication as expected. It reuses the password-lockout test base but focuses on ordinary login and recent-password behavior rather than full lockout cycles.

## Important APIs, Types, and Functions

- `BasicUserAuthTests` extends `BasePasswordTestCase`, inheriting account creation, credential cloning, lockout settings, LDAP/SAMR account validation, and login assertion helpers.
- `setUp()` initializes `host_url`, `host_url_ldaps`, `lp`, `global_creds`, and an admin `SamDB`, then delegates to the base setup that creates `lockout1krb5`, `lockout1ntlm`, and `lockout1simple`.
- `_test_login_basics(creds, simple=False)` is the core scenario used by all three tests.
- `test_login_basics_krb5()`, `test_login_basics_ntlm()`, and `test_login_basics_simple()` select credentials and transport.

## Control Flow

The core scenario picks the LDAP URL and expected `logonCount`/`lastLogon` relations based on the auth mechanism. Kerberos is expected to advance logon counters; NTLM and simple bind keep some counters equal in this test's expectations. It first checks the freshly prepared account state, then attempts a wrong password and expects `badPwdCount=1` and a newer `badPasswordTime`.

After a successful login with the correct password, the test changes the password four times through `userPassword` delete/add modifications on the user's own LDAP connection. It then discards credentials to avoid reusing cached Kerberos state and checks that an older password fails without incrementing `badPwdCount`. For the immediately previous password, Kerberos must fail while NTLM and simple bind are expected to succeed, matching the old-NT-hash grace behavior tested by Samba. Finally it verifies the newest password succeeds, while a too-old password fails and increments bad-password state.

## State and Persistence Behavior

The test mutates live user passwords and authentication metadata for accounts created by `BasePasswordTestCase`. Account attributes checked include `badPwdCount`, `badPasswordTime`, `logonCount`, `lastLogon`, `lastLogonTimestamp`, `userAccountControl`, and `msDS-User-Account-Control-Computed`. The base class restores domain lockout settings and deletes test users via cleanup. Kerberos credential objects are explicitly recreated between password attempts to avoid stale tickets affecting the result.

## Dependencies and Integration Points

The file depends on `password_lockout_base.BasePasswordTestCase`, `SamDB`, Samba credentials, `system_session`, and `UF_NORMAL_ACCOUNT`. It exercises DSDB password-change handling, LDAP bind paths for Kerberos/NTLM/simple bind, LDAPS requirements for simple bind, account metadata generation, and SAMR cross-checks performed inside `_check_account()`.

## Risks and Edge Cases

- Counter expectations differ by auth mechanism; changes in how NTLM/simple bind update `lastLogon` or `logonCount` will cause failures.
- Simple bind requires LDAPS and bind DN setup from the base class.
- Password history and old-password grace semantics are security-sensitive and intentionally asymmetric between Kerberos and NTLM.
- Cached Kerberos tickets can mask password changes if credentials are not recreated.

## Test Signals

The primary signals are wrong-password rejection, reset of `badPwdCount` after successful current-password login, successful chained `userPassword` changes, failure of too-old passwords, Kerberos rejection of the previous password, NTLM/simple acceptance of the previous password, and stable account-control flags throughout.
