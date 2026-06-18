# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_smb.c

## Purpose

`dcerpc_smb.c` implements DCE/RPC over SMB named pipes (`ncacn_np`). It opens a named pipe over an existing SMB1 or SMB2 tree/session and configures the generic DCE/RPC connection around the resulting `tstream_smbXcli_np` stream.

## Important APIs, Types, and Functions

`struct smb_private` stores the SMB session key, connection, session, tree connect, and timeout used for secondary named-pipe opens. Public APIs include `dcerpc_pipe_open_smb_send/recv()`, synchronous `dcerpc_pipe_open_smb()` for SMB1, `dcerpc_pipe_open_smb2()` for SMB2, and `dcerpc_secondary_smb_send/recv()`. `smb_session_key()` exposes the stored SMB application session key to RPC security code.

## Control Flow

The async open path normalizes pipe names by stripping `/pipe/`, `\\pipe\\`, and leading slash/backslash prefixes, captures SMB transport handles, records the remote server name, fetches the SMB application session key, and opens the named pipe with `tstream_smbXcli_np_open_send()`. Completion installs the stream, write queue, `NCACN_NP` transport type, Windows-compatible 4280 fragment limits, session-key callback, and transport encryption flag based on the SMB2 encryption cipher.

## State and Persistence Behavior

The file stores transport private state on `c->transport.private_data` and keeps the SMB session key in memory. It does not own or persist SMB sessions; it references caller-provided SMB handles. If no RPC binding exists, the synchronous helpers create an `ncacn_np:<remote>` binding.

## Dependencies and Integration Points

Dependencies include SMB raw and SMB2 client structures, `smbXcli` base/session helpers, `tstream_smbXcli_np`, tevent queues, and DCE/RPC connection internals. Secondary connection creation reuses this state through `dcerpc_secondary_smb_send()`.

## Risks and Test Signals

Risks include pipe-name normalization edge cases, absent user session keys, mismatched SMB encryption detection, lifetime coupling to SMB session/tree objects, and fragment-size assumptions. Tests should open RPC pipes over SMB1 and SMB2, with encrypted and unencrypted SMB3 sessions, missing session key behavior, secondary pipe reuse, and pipe names in all accepted slash forms.
