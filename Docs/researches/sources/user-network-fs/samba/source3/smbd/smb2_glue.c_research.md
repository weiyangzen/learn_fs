# sources/user-network-fs/samba/source3/smbd/smb2_glue.c

Purpose: provides SMB2-to-source3 compatibility glue so SMB2 handlers can reuse SMB1-era helpers that expect `struct smb_request`, connection fields, DFS flags, chain fsp state, and unread-byte tracking.

Important APIs: `smbd_smb2_fake_smb_request()` creates or reuses a fake `smb_request` for an SMB2 request and fills request time, vuid, tid, connection, xconn, session, PID, flags2, message ID, chain fsp, POSIX pathname state, and backpointer. `smbd_smb2_unread_bytes()` exposes `smb_request.unread_bytes`. `remove_smb2_chained_fsp()` clears compound chain fsp references when an fsp is freed.

Control flow: fake request creation pulls fields from the SMB2 header and current session/tree. It always enables Unicode, 32-bit errors, long paths, and long names, and only sets `FLAGS2_DFS_PATHNAMES` when the share is an msdfs root and the SMB2 DFS flag is present. Chain cleanup walks every SMB2 request on every client connection and clears both SMB2 and fake SMB1 chain pointers that reference the freed fsp.

State and persistence: state is in-memory and talloc-owned by the SMB2 request. No persistent storage is touched.

Dependencies and integration: used by create, flush, getinfo, ioctl, lock, notify, and other SMB2 handlers before calling source3 helpers. Depends on SMB2 header macros, loadparm DFS settings, `files_struct`, `smbd_server_connection`, and `smbXsrv_connection` lists.

Risks: incorrect fake request fields affect authorization, DFS parsing, POSIX path handling, deferred-open message IDs, or compound chains. Existing fake requests are reused, so callers must tolerate previously initialized fields.

Test signals: cover DFS flag propagation only on DFS shares, POSIX flag propagation, compound create/query chains, unread-byte propagation, and fsp free while compound or async requests retain chain pointers.
