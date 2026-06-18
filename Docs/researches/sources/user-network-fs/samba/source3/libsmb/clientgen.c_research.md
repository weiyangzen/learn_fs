# sources/user-network-fs/samba/source3/libsmb/clientgen.c

## Purpose

`clientgen.c` owns generic `cli_state` lifecycle and small connection helpers that are shared by the rest of source3 libsmb. It creates client state with negotiated capability preferences, tears it down safely, manipulates SMB1/SMB2 session and tree identifiers, tracks timeout/backup/case-sensitivity knobs, and implements SMB echo.

## Important APIs, Types, and Functions

- `cli_state_create()` allocates and initializes `struct cli_state`, chooses a client GUID, checks for setuid-root misuse, initializes server identity strings, maps command-line/environment flags into capabilities, creates `smbXcli_conn`, and creates an SMB1 session object.
- `cli_shutdown()` tears down one `cli_state` or an entire DFS-linked list headed by the given state.
- `_cli_shutdown()` closes RPC pipes, tree-disconnects when a tcon is active, disconnects the underlying `smbXcli_conn`, and frees the client state.
- `cli_set_timeout()`, `cli_set_backup_intent()`, `cli_set_case_sensitive()`, `cli_state_server_time()`, and `cli_state_available_size()` expose common connection settings/derived values.
- `cli_state_get_tid()`, `cli_state_set_tid()`, `cli_state_has_tcon()`, `cli_state_get_uid()`, `cli_state_set_uid()`, `cli_setpid()`, `cli_getpid()`, and `cli_state_get_vc_num()` abstract SMB1/SMB2 identifier access.
- `cli_state_save_tcon_share()` and `cli_state_restore_tcon_share()` temporarily detach and restore a tcon/share pair without freeing pipe-parented state.
- `cli_echo_send()`, `cli_echo_recv()`, and `cli_echo()` implement SMB echo for SMB1 and SMB2.

## Control Flow

Creation begins by selecting a client GUID from global override, loadparm value, or `GUID_random()`. It rejects setuid-root execution, allocates `cli_state`, seeds server-domain/OS/type strings, sets default timeout and DOS-error mapping, then interprets environment variables and connection flags for forced DOS errors, ASCII, SPNEGO suppression, oplocks, and level-II oplocks. Signing defaults are resolved through loadparm, with IPC default biased toward required signing. SMB1 capability bits are built from large files, NT SMBs, DFS, large read/write, LWIO, status32, unicode, extended security, and oplocks. SMB2/3 capabilities come from `SMB2_CAP_ALL` and parsed SMB 3.1.1 signing/encryption/QUIC policy. Finally `smbXcli_conn_create()` and `smbXcli_session_create()` attach transport and session objects.

Shutdown closes all open pipes by freeing list nodes, sends `cli_tdis()` if a tree connection exists, disconnects the transport, and frees the state. When the target is the head of a DFS connection list, `cli_shutdown()` iterates and frees subsidiary DFS connections before freeing the head.

Echo dispatches by negotiated protocol. SMB2 ignores the SMB1 echo count/data and calls `smb2cli_echo_send()`, while SMB1 uses `smb1cli_echo_send()`. The synchronous wrapper refuses to run while async calls are in flight on the connection.

## State and Persistence Behavior

This module is entirely in-memory. It initializes and mutates `cli_state` fields such as `timeout`, `backup_intent`, `use_oplocks`, `map_dos_errors`, `smb1.pid`, `smb1.vc_num`, `smb1.session`, `smb1.tcon`, `smb2.tcon`, `share`, and the linked `pipe_list`. It also reads process environment (`CLI_FORCE_DOSERR`, `CLI_FORCE_ASCII`) and Samba configuration. The tcon save/restore helpers deliberately detach raw tcon pointers rather than deep-copying to preserve open pipe parentage.

## Dependencies and Integration Points

The file depends on Samba loadparm, signing/sealing policy, SMBX transport/session/tcon helpers, SMB2 negotiate contexts, NDR GUID support, async SMB helpers, talloc, and tevent. Other libsmb modules rely on these helpers to avoid protocol-specific direct access to tcon ids, encryption state, server time, and connection shutdown.

## Risks and Edge Cases

- Sync helpers must keep rejecting use while async operations are outstanding; violating that can corrupt request sequencing.
- `cli_state_restore_tcon()` frees any replacement tcon before restoring the saved one. Callers must pair save/restore precisely.
- Capability flags in `cli_state_create()` drive negotiation behavior across many clients; environment-controlled force flags are useful tests but risky if assumed unavailable.
- `cli_shutdown()` uses list-head detection; callers holding non-head DFS children need to understand that shutting down the head tears down the whole list.
- IPC signing defaults and encryption algorithms are security-sensitive and tied to current loadparm behavior.

## Test Signals

Tests should verify flag-to-capability mapping, setuid-root rejection, GUID override behavior, signing defaults for IPC/default modes, forced ASCII/DOS env behavior, SMB1 versus SMB2 tcon id getters/setters, tcon save/restore preserving share strings, DFS-list shutdown, encryption-on checks for SMB1/SMB2, echo sync rejection during async calls, and successful SMB1/SMB2 echo paths.
