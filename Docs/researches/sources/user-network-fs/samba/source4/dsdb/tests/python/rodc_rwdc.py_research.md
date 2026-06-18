# sources/user-network-fs/samba/source4/dsdb/tests/python/rodc_rwdc.py

## Purpose

This executable integration suite tests credential, password, lockout, replication, and referral behavior between a read-only domain controller and a writable domain controller. It verifies that RODC credential caching, reveal-on-demand policy, password changes on the RWDC, logon forwarding, lockout counters, replicated object visibility, and LDAP simple/SASL authentication remain consistent across forced replication boundaries.

## Important APIs, Types, and Functions

Top-level helpers:

- `adjust_cmd_for_py_version(parts)` prepends `$PYTHON` to subprocess commands when requested.
- `passwd_encode(pw)` encodes quoted UTF-16LE passwords for LDIF-style `unicodePwd` use.
- `make_creds(username, password, kerberos_state=None, simple_dn=None)` creates sealed credentials based on global command-line credentials, optionally forcing Kerberos/NTLM or setting a simple-bind DN.
- `set_auto_replication(dc, allow)` runs `bin/samba-tool drs options` to enable or disable inbound/outbound replication on a DC. It tolerates LDAP referral errors when the target behaves as an RODC.
- `preload_rodc_user(user_dn)` temporarily enables RWDC replication, runs `samba-tool rodc preload`, then disables replication again.
- `get_server_ref_from_samdb(samdb)` resolves a DC server object's `serverReference`.

There are two main test classes, both derived from `password_lockout_base.BasePasswordTestCase`:

- `RodcRwdcCachedTests` focuses on cached credentials, password cache flushing, SendToSam behavior, and lockout propagation for users whose secrets are preloaded or not revealed.
- `RodcRwdcTests` focuses on regular RODC/RWDC replication, referred/replicated object behavior, LDAP password changes, reveal-on-demand interactions, and base password-lockout/multiple-logon flows through an RODC.

Both classes implement `force_replication()` with `samba-tool drs replicate RODC RWDC <base> --sync-forced`, maintain `rodc_db` and `rwdc_db` `SamDB` connections, wire BasePasswordTestCase fields (`lp`, `global_creds`, `host`, `host_url`, `ldb`), and restore automatic replication in teardown.

## Control Flow

The module parses `<rodc host> <rwdc host>`, obtains sealed credentials, turns automatic replication on before and after `TestProgram`, and each test setup disables RWDC automatic replication to make synchronization explicit.

`RodcRwdcCachedTests` setup first initializes against the RWDC for shared lockout fixture creation, then switches the host URLs to the RODC. It caches original `dSHeuristics`, sets `000000001`, disables auto replication, and forces initial sync. Its tests:

- `test_cache_and_flush_password()` proves preloading exposes a user's `unicodePwd` to local system search, then changing the password on RWDC and forced replication removes the cached secret.
- `test_login_lockout_krb5()` and `test_login_lockout_ntlm()` preload a user, add it to the RODC reveal-on-demand group, optionally adjust lockout timing, and run `_test_login_lockout_rodc_rwdc()`.
- `test_login_lockout_not_revealed()` verifies a preloaded but non-revealed user can report bad-password state to the RWDC while RODC-local `badPwdCount` resets on successful authentication.
- `_test_login_lockout_rodc_rwdc()` performs a long sequence of wrong and correct password attempts, asserting `badPwdCount`, `badPasswordTime`, `lockoutTime`, `msDSUserAccountControlComputed`, `lastLogon`, and effective counter behavior before, during, and after lockout and observation-window expiry.

`RodcRwdcTests` setup similarly creates RODC/RWDC connections and then points BasePasswordTestCase operations at the RODC. Its test flow includes:

- `_test_add()` proving objects added to RWDC are absent on RODC before replication and present after forced replication, including optional cross-NC searches with `search_options:1:2`.
- Add/modify/delete replication tests for OUs, users, groups, `NTDSConnection`, regular replicated attributes, and object deletion.
- `_new_user()` creating and enabling a user on RWDC with a starting password.
- `_test_ldap_change_password()` changing a user's password repeatedly on RWDC, then checking old and new credentials against RODC and RWDC before and after replication, including NTLM and simple bind invalid-credential expectations.
- `_test_ldap_change_password_reveal_on_demand()` adding a new user to the RODC reveal-on-demand group, preloading the secret, changing password on RWDC, and verifying the cached old password and forwarded new-password behavior.
- Lockout and multiple-logon tests that preload fixture users, seed failure/success authentication through the RODC, then delegate to `BasePasswordTestCase` helpers.

## State and Persistence Behavior

The suite manipulates live DC replication state. It disables and re-enables inbound/outbound replication options, runs forced replication, preloads RODC secrets, changes domain `dSHeuristics`, creates users and directory objects on the RWDC, modifies reveal-on-demand group membership, changes passwords, and adjusts lockout policy fields. Teardown restores RWDC `dSHeuristics`, sets credentials back to non-Kerberos in `RodcRwdcTests`, and re-enables auto replication.

State visibility is intentionally staged: tests often assert absence on the RODC before `force_replication()` and presence afterward. Credential cache state is checked through a local system `SamDB` search for `unicodePwd`; password changes on the RWDC are expected to flush RODC-cached secrets after replication. Time sleeps account for delayed SendToSam/Kerberos bad-password propagation and lockout windows.

## Dependencies and Integration Points

The file depends on Samba's `SamDB`, credentials stack, gensec sealing, SAMR RPC client, DSDB constants, `password_lockout_base.BasePasswordTestCase`, `samba-tool drs` and `samba-tool rodc preload` subprocesses, LDAP/LDAPS authentication behavior, reveal-on-demand RODC attributes, and AD replication topology. It integrates Python test code with external command-line replication controls, making it a full system integration test rather than a unit test.

## Risks and Edge Cases

The suite is sensitive to environment topology: it requires a real RODC/RWDC pair, working `bin/samba-tool`, credentials with rights to change replication options and preload secrets, and predictable replication timing. Subprocess failures raise a generic `RodcRwdcTestException` after printing stdout/stderr, so diagnostics rely on test logs. Several tests sleep for fixed periods to wait for SendToSam or lockout windows; slow or overloaded test environments can be flaky.

Because automatic replication is disabled during tests, teardown failure can leave replication options altered. Tests also modify reveal-on-demand group membership, password policy, users, and temporary objects. The code uses unique tags and BasePasswordTestCase cleanup, but the blast radius is larger than pure LDAP unit tests.

Security-sensitive risks under test include stale RODC password caches after RWDC password changes, unauthorized SendToSam updates for users outside reveal policy, divergent lockout counters between RODC and RWDC, and authentication accepting too-old passwords after multiple changes.

## Test Signals

Passing results signal that RODC credential caching, password-cache invalidation, reveal-on-demand policy, lockout propagation, LDAP authentication forwarding, and object replication behave coherently across forced RWDC-to-RODC synchronization. Failures point to regressions in replication control, secret preloading, SendToSam, password history visibility, lockout computation, referral/replication behavior, or RODC/RWDC authentication routing.
