# sources/user-network-fs/samba/source4/dsdb/tests/python/password_lockout_base.py

## Purpose

`password_lockout_base.py` provides the shared test harness for lockout and login tests. It creates test users, configures domain lockout policy, provides credential factories and login assertions, and most importantly cross-checks LDAP account attributes against SAMR account information so higher-level tests validate both directory and RPC views of account state.

## Important APIs, Types, and Functions

- `BasePasswordTestCase` extends `samba.tests.password_test.PasswordTestCase`.
- `_open_samr_user()` unpacks `objectSid`, verifies the domain SID, and opens the user by RID over SAMR.
- `_check_attribute()` implements comparison modes: `equal`, `greater`, `less`, `present`, `absent`, `ignore`, and `None` for missing.
- `_check_account_initial()` and `_check_account()` validate LDAP state and SAMR `QueryUserInfo` levels 3, 5, 16, and 21.
- `update_lockout_settings()` writes `lockoutDuration`, `lockoutThreshold`, and `lockOutObservationWindow` on the domain DN using negative 100ns tick values.
- `_readd_user()` deletes/recreates a user, sets an initial password, enables the account, performs a failure/success cycle to seed `badPasswordTime`, and supports simple-bind setup.
- `assertLoginFailure()` and `assertLoginSuccess()` wrap `SamDB` bind attempts.
- `setUp()` stores original domain lockout settings for cleanup, applies test policy, opens SAMR handles, and creates Kerberos, NTLM, and simple-bind test users.
- `_test_login_lockout()` and `_test_multiple_logon()` are reusable scenarios consumed by `password_lockout.py`.

## Control Flow

Setup begins by enabling sealed credentials, constructing a template credential object, reading current domain lockout attributes, and registering a cleanup LDIF to restore them. It applies a threshold of three, short duration/window defaults unless subclasses override them, calls `allow_password_changes()`, opens SAMR domain handles, and recreates three test users. `_readd_user()` initializes each account through LDAP, validates the all-zero account state, deliberately fails one login to create `badPasswordTime`, then performs a successful bind to reset counters.

`_check_account()` sleeps briefly to avoid timestamp-resolution races, searches LDAP for account state, validates requested attributes, opens the matching SAMR user, and maps `userAccountControl` plus computed flags to expected SAMR account flags. It then checks bad-password count, last-logon, and logon-count values across SAMR info classes and re-reads LDAP to ensure SAMR queries did not mutate directory state.

`_test_login_lockout()` drives the canonical login lockout sequence: wrong password, correct password reset, repeated wrong passwords until threshold, extra wrong/correct attempts while locked, optional sleep past lockout duration, correct login after computed unlock, observation-window expiry, and final correct login reset. `_test_multiple_logon()` checks repeated successful logons do not create bad-password state and update counters according to auth mechanism.

## State and Persistence Behavior

The base class writes domain lockout policy and test user objects in the live directory. It persists and later restores original domain settings with cleanup handlers. It creates LDAP connections and SAMR handles as test state, deletes the main LDAP connection in cleanup, and relies on inherited cleanup to run even after assertions. Account state under test includes stored LDAP attributes, generated computed flags, and SAMR's derived account-info fields.

## Dependencies and Integration Points

The file depends on Samba credentials, GENSEC sealing, `SamDB`, LDB primitives, `samba.dsdb`, `samr`, `security.dom_sid`, `ndr_unpack`, `delete_force`, and `PasswordTestCase`. It integrates domain policy writes, password modification modules, LDAP bind authentication, generated account-control computation, and SAMR RPC views of the same users.

## Risks and Edge Cases

- Short sleep windows are vulnerable to slow hosts or coarse timestamp behavior.
- Cleanup correctness is critical because domain lockout policy is global.
- `_check_account()` assumes a one-to-one mapping between LDAP state and SAMR info classes; intentional SAMR behavior changes require test updates.
- Kerberos and NTLM/simple bind have different expected logon counter behavior.
- Simple bind requires LDAPS and bind DN handling in `_readd_user()`.

## Test Signals

The strongest signals are LDAP/SAMR agreement, restoration of domain policy after tests, correct computed lockout and password-expired flags, stored versus effective bad-password count behavior, successful creation/reset of test users, and stable logon metadata across failure and success sequences.
