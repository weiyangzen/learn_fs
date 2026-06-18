# sources/user-network-fs/samba/source3/smbd/smb2_ioctl_private.h

Purpose: defines the private shared state and dispatcher prototypes for SMB2 IOCTL device-specific modules.

Important APIs and types: `struct smbd_smb2_ioctl_state` carries the parent SMB2 request, fake SMB1 request, optional fsp, input blob, max output length, output blob, response body padding, and disconnect flag. It declares `smb2_ioctl_dfs()`, `smb2_ioctl_filesys()`, `smb2_ioctl_named_pipe()`, `smb2_ioctl_network_fs()`, and `smb2_ioctl_smbtorture()`.

Control flow and integration: `smb2_ioctl.c` allocates and fills this state, then dispatches by FSCTL device type. Submodules mutate output, padding, or disconnect fields and complete or error the shared tevent request.

State and persistence: per-request transient state only. Output ownership is talloc-based and later stolen into the SMB2 response.

Dependencies: relies on normal Samba include ordering for `DATA_BLOB`, `files_struct`, `tevent_req`, `tevent_context`, `smb_request`, and `smbd_smb2_request`.

Risks: all IOCTL modules share this struct, so ownership changes or rare fields like `body_padding`/`disconnect` can break cross-module behavior. Prototype drift is build-detected, but completion semantics are not.

Test signals: build all IOCTL modules and run DFS, filesystem, named-pipe, network FS, and smbtorture FSCTL tests to verify shared output, disconnect, and padding propagation.
