<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/secleak.c -->
# sources/user-network-fs/samba/source4/torture/smb2/secleak.c

## Purpose
`secleak.c` is an SMB2 security memory leak torture helper. It repeatedly attempts failed session setup with deliberately invalid credentials and prints talloc allocation reports, allowing developers to inspect whether failed authentication leaks client-side or security-related allocations over time.

## Important APIs, Types, And Functions
`try_failed_login()` creates a new SMB2 session on the existing transport, builds invalid `struct cli_credentials`, and calls `smb2_session_setup_spnego()`. `torture_smb2_sec_leak()` is the exported test entry point used by the SMB2 torture suite. Important APIs and types include `struct smb2_tree`, `struct smb2_session`, `smb2_session_init()`, `smb2cli_session_current_id()`, `cli_credentials_init()`, `cli_credentials_set_conf()`, `cli_credentials_set_domain()`, `cli_credentials_set_username()`, `cli_credentials_set_password()`, `smb2_session_setup_spnego()`, `talloc_steal()`, `talloc_report()`, and `time_mono()`.

## Control Flow
`torture_smb2_sec_leak()` reads `torture:timelimit`, defaulting to 20 seconds, and loops until monotonic time reaches that deadline. Each iteration calls `try_failed_login()` and asserts the result. After every failed login attempt it prints a talloc report to stdout.

Inside `try_failed_login()`, a temporary SMB2 session is initialized against the tree's transport and uses the current session id as the previous/session context. Invalid domain, username, and password values are specified. The expected result of SPNEGO session setup is `NT_STATUS_LOGON_FAILURE`; success or a different status is treated as a test failure. Before freeing the temporary session, the transport is stolen back to the original tree session because `smb2_session_init()` takes ownership of it.

## State And Persistence
The test does not create files. It repeatedly mutates client-side session/transport ownership and authentication state. The crucial persistent pointer is `tree->session->transport`; without stealing it back before freeing the temporary session, later iterations would hold an invalid transport pointer. The allocation reports expose whether repeated failure paths grow talloc trees.

## Dependencies And Integration Points
The file depends on Samba's SMB2 session setup, GENSEC settings, credential handling, talloc ownership model, and torture context settings. It is meant to run against a live authenticated SMB2 tree while probing failed secondary session setup behavior.

## Risks
Because the test intentionally performs many failed logins, it can trigger account lockout or audit noise on real authentication backends if invalid attempts are counted. It is also sensitive to the talloc ownership contract around transports; future changes to `smb2_session_init()` ownership semantics could make the steal-back workaround wrong. The output is diagnostic rather than a precise automated leak detector unless compared externally.

## Test Signals
Expected behavior is repeated `NT_STATUS_LOGON_FAILURE` with no crash and stable talloc report shape over the configured time window. A successful login with invalid credentials, growing allocation reports, transport invalidation on the next iteration, or statuses other than logon failure indicate a regression or environment issue.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/secleak.c -->
