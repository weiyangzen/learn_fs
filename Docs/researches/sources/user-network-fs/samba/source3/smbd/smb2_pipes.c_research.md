# sources/user-network-fs/samba/source3/smbd/smb2_pipes.c

## Purpose
This file opens named pipe fake files for SMB requests. It adapts an SMB request and pipe name into a `files_struct` backed by the RPC named-pipe subsystem rather than a real filesystem fd, and adds SMB3 encryption context information to the session token when encrypted SMB2 pipe access is used.

## Important APIs, Types, And Functions
`open_np_file()` is the only function. It allocates a new file with `file_new()`, marks it fd-less via `fsp_set_fd(fsp, -1)`, disables byte-range locking, sets read/write data access, stores the pipe basename with `fsp_set_smb_fname()`, and finally calls `np_open()` to create `fsp->fake_file_handle`. When the SMB2 request was encrypted, it uses `copy_session_info()`, edits the copied `security_token`, appends an SMB3 SID made from `global_sid_Samba_SMB3`, dialect, encryption-required marker, and cipher, and marks `fsp->fsp_flags.encryption_required`.

## Control Flow
The function is linear: allocate fsp, initialize fsp fields from `smb_request` and connection, copy the basename, optionally augment session security for encrypted SMB2, then call `np_open()` with remote/local addresses, event context, messaging context, DCE context, and the selected session info. Every allocation or pipe-open failure frees the partially created fsp before returning an NTSTATUS.

## State And Persistence
There is no disk persistence. State is the live fake file handle, fsp metadata, copied session info for encrypted requests, and the named-pipe server state behind `np_open()`. The SMB3 SID insertion is scoped to the copied session info, not the original connection session.

## Dependencies And Integration Points
This code integrates smbd file-handle management with `rpc_server/srv_pipe_hnd.h`, DCE/RPC helpers, auth token utilities, connection addresses, and SMB2 encryption metadata. The resulting fake file is consumed by SMB2 read/write/ioctl paths and named-pipe RPC server code.

## Risks And Test Signals
Tests should verify successful pipe open, cleanup on every allocation and `np_open()` failure, encrypted SMB2 pipe open adding exactly one SMB3 SID, rejection if an SMB3 SID is already present, correct dialect/encryption/cipher RID construction, and `encryption_required` propagation to later pipe I/O. A key risk is accidentally mutating shared session security instead of the per-fsp copy, or allowing duplicate SMB3 marker SIDs.
