# sources/user-network-fs/samba/source3/libsmb/passchange.c

## Purpose
This file implements `remote_password_change`, the client-side routine for changing a user's password on a remote SMB server. It negotiates an IPC connection, tries secure SAMR password-change RPCs, handles password-expired flows, and optionally falls back to the legacy RAP/LanMan password change method when configured.

## Important APIs, Types, And Functions
The exported function is `remote_password_change`. It uses `cli_connect_nb`, `cli_session_creds_init`, `smbXcli_negprot`, `cli_session_setup_creds`, `cli_session_setup_anon`, `cli_tree_connect`, `cli_rpc_pipe_open_with_creds`, `cli_rpc_pipe_open_noauth`, `dcerpc_samr_chgpasswd_user4`, `rpccli_samr_chgpasswd_user2`, `cli_oem_change_password`, and `cli_shutdown`.

## Control Flow
The function connects to the remote machine's NetBIOS server name, creates credentials from domain/user/old password, negotiates the configured IPC protocol range, and attempts authenticated session setup. If the server returns `PASSWORD_MUST_CHANGE` or `PASSWORD_EXPIRED`, it records that state and reconnects the session anonymously so the password-change RPC can proceed.

After connecting to `IPC$`, it opens a SAMR pipe. Normal flow uses NTLMSSP with privacy so the password is protected; must-change flow uses an anonymous SAMR pipe because authenticated bind would fail in the same way as session setup. If pipe open fails and `client lanman auth` allows it, the function falls back to `cli_oem_change_password`; otherwise it returns an explanatory error.

The preferred password operation is `samr_ChangePasswordUser4`. If the server lacks that procedure and weak crypto is disallowed, the function returns `NT_STATUS_STRONG_CRYPTO_NOT_SUPPORTED` instead of falling back to RC4-based methods. Otherwise it tries `samr_ChangePasswordUser2`, then an anonymous pipe with `ChangePasswordUser2`, and finally the RAP/LanMan method if enabled.

## State And Persistence
The only intended persistent effect is the password change on the remote account. Local state is transient connection, credential, and pipe state. Human-readable errors are allocated with `asprintf` into `err_str`, and the SMB connection is shut down on every return path after a successful connect.

## Dependencies And Integration Points
This file integrates NetBIOS connection setup, SMB protocol negotiation, cli credentials, IPC tree connect, SAMR RPC clients, generated NDR SAMR definitions, Samba loadparm settings for transports/protocols/LanMan/weak crypto, and friendly NT error formatting. It is a high-level helper for tools that need password change without manually driving SAMR.

## Risks And Edge Cases
Security-sensitive fallback behavior is central: weak crypto policy prevents fallback from `ChangePasswordUser4` to older RC4-style paths for unsupported procedures, while LanMan fallback is separately gated by `lp_client_lanman_auth()`. Error string allocation failures deliberately leave `*err_str = NULL`. One `asprintf` check after `cli_tree_connect` tests nonzero rather than `-1`, which can clear a successfully allocated error string. Anonymous fallback may be required for expired passwords but should not be used when authenticated secure RPC succeeds.

## Test Signals
Tests should cover connection failure including NetBIOS-disabled `NOT_SUPPORTED`, negotiate failure, normal authenticated SAMR `ChangePasswordUser4`, expired-password anonymous flow, unsupported procnum with weak crypto disallowed, `ChangePasswordUser2` fallback, anonymous SAMR fallback after access denied, LanMan enabled/disabled behavior, password policy rejection messages, and cleanup of `cli` on all error paths.
