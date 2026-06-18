# sources/user-network-fs/samba/source4/torture/smb2/tcon.c

## Purpose
`tcon.c` implements a focused SMB2 tree-connect identity test. It verifies that file handles are scoped correctly to the tree ID and session ID that opened them, and that a server rejects writes performed through an unrelated tree connect, an invalid tree ID, or an invalid session ID.

## Important APIs, Types, and Functions
The central exported test function is `run_tcon_test(struct torture_context *tctx, struct smb2_tree *tree)`. The local helper `smb2cli_session_set_id()` wraps `smb2cli_session_set_id_and_flags()` so the test can temporarily alter only the session ID while preserving session flags. The test uses `smb2_create`, `smb2_util_write`, `smb2_util_close`, `smb2_util_unlink`, `torture_smb2_tree_connect`, `smb2cli_tcon_current_id`, `smb2cli_tcon_set_id`, and `smb2cli_session_current_id`.

## Control Flow
The test removes any stale `tcontest.tmp`, creates the file on the supplied tree with read/write access and broad share access, records the valid tree ID and session ID, and performs an initial write to prove the handle is usable. It then opens a second tree connect on the same session and derives an invalid tree ID and invalid session ID.

The negative checks deliberately mutate the second tree's IDs. First it uses the second tree's valid TID with the first tree's file handle and expects the write to fail. Next it sets an arbitrary invalid TID and again expects failure. Finally it changes the session ID to a different value while setting the TID back to the first tree ID and expects the server to reject the write. After the negative checks, the original session and tree IDs are restored, the handle is closed, and the file is removed.

## State and Persistence Behavior
The only durable server object is `tcontest.tmp`, which is created, written, closed, and unlinked. More important is transient connection state: the test mutates client-side tree and session IDs to send intentionally invalid SMB2 requests. That state is restored before the final close to avoid poisoning later tests on the same connection.

## Dependencies and Integration Points
This file depends on low-level SMB2 client ID accessors from `smbXcli_base`, SMB2 torture connection helpers, resolver/event/loadparm context includes, and the standard torture result path. The function is registered elsewhere in the SMB2 suite through generated prototypes from `torture/smb2/proto.h`.

## Risks
Because it changes in-memory IDs on a live client object, failed cleanup could leave the connection in an invalid state for subsequent tests. The expected failures are protocol-security critical: accepting any of these writes would indicate handle authorization is not bound to the correct tree/session identity.

## Test Signals
The primary signals are `NT_STATUS_OK` for initial create/write/close and non-OK statuses for writes through the wrong TID, invalid TID, and invalid VUID/session ID. Any successful negative write is a torture failure.
