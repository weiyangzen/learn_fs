# sources/user-network-fs/samba/source4/torture/basic/secleak.c

## Purpose
This file repeatedly attempts failed SMB session setup with invalid credentials to expose security/authentication memory leaks.

## Important APIs, types, and functions
Local `try_failed_login()` creates a new `smbcli_session`, builds `struct smb_composite_sesssetup`, initializes credentials, sets an invalid domain/user/password, calls `smb_composite_sesssetup()`, and frees the session. Exported `torture_sec_leak()` loops this helper until a configured time limit expires and calls `talloc_report()`.

## Control flow
For each iteration, the test obtains SMB session options from `lp_ctx`, attaches to the existing transport, configures credentials with invalid values, performs composite session setup, and expects failure. A successful invalid login is a hard failure. The outer loop runs until `time_mono()` exceeds `timelimit` (default 20 seconds).

## State and persistence
The test creates no files. State under test is client/server authentication allocation behavior and cleanup after failed session setup. It prints talloc reports to stdout to show memory growth.

## Dependencies and integration points
It depends on `auth/credentials`, gensec settings, composite SMB session setup, and the existing negotiated transport. It is a runtime diagnostic rather than a file operation test.

## Risks
The test can generate many authentication failures and logs. It does not automatically quantify memory growth; humans or log tooling must interpret `talloc_report()` output. The invalid credential path must remain invalid in the environment.

## Test signals
Signals are any accepted invalid session setup, increasing talloc allocation reports across iterations, or unexpected transport/session failures unrelated to authentication rejection.
