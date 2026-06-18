# sources/user-network-fs/samba/source4/dsdb/tests/python/password_lockout.py

## Purpose

`password_lockout.py` is Samba's broad AD account-lockout integration suite. It verifies lockout state transitions for LDAP login failures, `userPassword` and `unicodePwd` password changes with bad old passwords, SAMR password change/set operations, Protected Users behavior, PSO-driven lockout policy, explicit unlock paths, default long-duration settings, and observation-window behavior.

## Important APIs, Types, and Functions

- `PasswordTests` extends `BasePasswordTestCase`, creates admin and user LDAP connections, and adds secondary Kerberos/NTLM users used to perform password changes.
- `use_pso_lockout_settings()` creates a `PasswordSettings` object with lockout settings, applies it to a user, and changes domain defaults to prove the PSO is the effective policy.
- `_reset_samr()` clears `samr.ACB_AUTOLOCK` through SAMR.
- `PasswordTestsWithoutSleep` uses long lockout windows and tests unlock methods without waiting: LDAP `lockoutTime=0`, LDAP `userAccountControl`, SAMR, and `samba-tool user unlock`.
- `_test_userPassword_lockout_with_clear_change()` drives bad old-password changes against `userPassword`.
- `_test_samr_password_change()` drives `Net.change_password()` failures and lockout.
- Protected Users tests modify the domain Protected Users group and check NTLM/SAMR restrictions do not increment lockout.
- `PasswordTestsWithSleep` covers `unicodePwd`, full login lockout/unlock waits, PSO login lockout, and observation-window expiration.
- `PasswordTestsWithDefaults` checks lockout with default-length windows without sleeping until expiry.

## Control Flow

Base setup creates primary lockout users. `PasswordTests.setUp()` adds secondary users and binds as them. Cleartext `userPassword` tests start from a clean account, attempt password changes with wrong old passwords until `badPwdCount` reaches the threshold, and assert transition from Windows error `00000056` to lockout error `00000775`. Once locked, both wrong and correct old-password changes must fail. The test then proves password reset alone does not unlock the account, verifies locked users appear in `samba-tool user list --locked-only`, unlocks via the selected method, and confirms bad-password counters and `lockoutTime` reset.

SAMR tests use `samba.net.Net` as another user. A correct change proves the path works, then repeated bad old passwords must return `NT_STATUS_WRONG_PASSWORD` until the threshold and `NT_STATUS_ACCOUNT_LOCKED_OUT` after lockout. Unlocking through SAMR must reset bad counts and allow a subsequent successful change.

Protected Users tests add the test user to the Protected Users group. NTLM logins with wrong passwords must fail but keep `badPwdCount=0` and avoid `lockoutTime`. SAMR change/set password operations for protected users must return `NT_STATUS_ACCOUNT_RESTRICTION` without lockout, while LDAP password changes remain possible where expected.

`unicodePwd` tests mirror the cleartext path with UTF-16LE quoted base64 password values and include checks that SAMR unlock has no effect before actual lockout. Login lockout tests are inherited from the base class and run with sleeps to observe computed unlock after duration and bad-count decay after the observation window. The default class repeats key login lockout checks with long default durations but stops once lockout is reached.

## State and Persistence Behavior

The module heavily mutates domain and account state: lockout policy attributes, PSOs, test users, user passwords, `badPwdCount`, `badPasswordTime`, `lockoutTime`, `lastLogon`, `lastLogonTimestamp`, group membership, and SAMR account flags. Cleanup from the base class restores domain lockout settings and deletes test users; PSOs are cleaned with `addCleanup`. Some tests temporarily modify Protected Users membership and store an LDAP diff for cleanup or manual reversal.

Lockout state is persisted in LDAP attributes but also exposed through generated `msDS-User-Account-Control-Computed` and SAMR `acct_flags`. The tests distinguish stored `badPwdCount` from effective bad-password count after lockout duration or observation-window expiry.

## Dependencies and Integration Points

The suite depends on `password_lockout_base`, `SamDB`, LDB errors, `samba.dsdb` flags, `samr`, `security`, `PasswordSettings`, `Net`, `samba_tool`, `subprocess`, `ntstatus`, and UTF-16LE/base64 `unicodePwd` encoding. It integrates LDAP bind/authentication, DSDB password modification modules, PSO resultant policy, SAMR Query/SetUserInfo, Net password RPCs, command-line `samba-tool`, and special Protected Users restrictions.

## Risks and Edge Cases

- Timing-sensitive sleeps can flap on slow systems; no-sleep classes use long windows to reduce this.
- The file assumes error data strings such as `00000056`, `00000775`, and `0000052D` remain stable.
- Tests mutate Protected Users membership and user passwords; interrupted runs may leave accounts in altered states until cleanup.
- Kerberos and NTLM have different counter expectations, especially `logonCount` and `lastLogon`.
- PSO tests intentionally set domain lockout policy to different values; failures in cleanup can affect unrelated authentication tests.
- `samba-tool` subprocess tests depend on `bin/samba-tool` and command-line credential formatting.

## Test Signals

Important signals are exact bad-password count progression, `lockoutTime` creation and clearing, `msDS-User-Account-Control-Computed` lockout bit, SAMR `ACB_AUTOLOCK`, distinction between stored and effective bad counts, correct unlock behavior for all methods, PSO policy overriding domain policy, Protected Users avoiding lockout, expected NTSTATUS/LDB error codes, and successful post-unlock password changes.
