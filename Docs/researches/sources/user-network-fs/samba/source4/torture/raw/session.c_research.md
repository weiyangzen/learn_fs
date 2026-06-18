# sources/user-network-fs/samba/source4/torture/raw/session.c

## Purpose
This file implements raw SMB session setup, reauthentication, and Kerberos session-expiry tests. It verifies that reauth can preserve the VUID and open handles, that changing credentials affects access checks on existing/opened objects, and that dynamic reauth handles expired Kerberos sessions as expected.

## Important APIs, Types, And Functions
The suite factory `torture_raw_session()` registers `test_session_reauth1`, `test_session_reauth2`, and `test_session_expire1`. The tests use `struct smb_composite_sesssetup`, `smb_composite_sesssetup()`, command-line credentials from `samba_cmdline_get_creds()`, anonymous credentials from `cli_credentials_init_anon()`, and raw file operations including `smb_raw_open`, `smb_raw_open_send/recv`, `smb_raw_fileinfo`, and `smbcli_nt_delete_on_close()`.

`test_session_reauth2_oplock_timeout()` is an oplock break handler that returns true, allowing the test to proceed through a conflicting open. `test_session_expire1()` additionally uses `smbcli_full_connection()`, loadparm session options, Kerberos credential state, ccache invalidation, and the `CAP_DYNAMIC_REAUTH` capability flag.

## Control Flow
`test_session_reauth1()` creates a random delete-on-close file, writes random data, performs a second session setup using the normal credentials, asserts that the returned VUID equals the original VUID, and reads the still-open file to prove handle continuity.

`test_session_reauth2()` opens a file with a batch oplock, queues a conflicting open, sets delete-on-close on the original handle, reauthenticates the same session as anonymous, closes the first handle, receives the queued open, writes data, and verifies querying the security descriptor owner fails with `ACCESS_DENIED`. It then reauthenticates back to the command-line credentials using the same VUID, repeats the security descriptor query successfully, marks delete-on-close, and closes.

`test_session_expire1()` requires `--use-kerberos=required`, sets a short requested GSSAPI lifetime, opens a new SMB connection, creates a delete-on-close file, and queries access information across sleeps. With `CAP_DYNAMIC_REAUTH`, it expects operations after expiry to return `NT_STATUS_NETWORK_SESSION_EXPIRED`, then reauthenticates and repeats. Without `CAP_DYNAMIC_REAUTH`, it expects reauth to keep subsequent operations OK through shorter sleeps. It restores the GSSAPI lifetime option on exit.

## State And Persistence Behavior
The tests create random-named delete-on-close files and rely on open handles for cleanup. They mutate the authenticated identity associated with an existing SMB session while preserving VUID, manipulate oplock/conflicting-open state, invalidate the Kerberos credential cache, and temporarily set `gensec_gssapi:requested_life_time`. `test_session_expire1()` owns a separate full SMB connection and frees it at cleanup.

## Dependencies And Integration Points
Dependencies include composite session setup, raw SMB file operations, oplock callbacks, command-line credential plumbing, Kerberos configuration, loadparm options, resolver and event contexts, and NT security descriptor query support. The suite integrates through `raw.c` as the nested `session` suite.

## Risks And Edge Cases
These tests are authentication-environment-sensitive. `expire1` is skipped unless Kerberos is required and includes real sleeps, making it slower and time-dependent. Reauth behavior is subtle because VUID preservation, credential replacement, open handles, oplock breaks, and delete-on-close interact. Anonymous access expectations can differ by server policy, but the test specifically requires security descriptor owner query denial after anonymous reauth.

## Test Signals
Success signals include unchanged VUIDs across reauth, readable data through an open handle after reauth, anonymous `ACCESS_DENIED` for owner security descriptor query, restored access after credential reauth, expected `NETWORK_SESSION_EXPIRED` with dynamic reauth, and continued OK operations without dynamic expiry signaling. Failures identify the session setup phase, file operation, VUID comparison, or expiry expectation that failed.
