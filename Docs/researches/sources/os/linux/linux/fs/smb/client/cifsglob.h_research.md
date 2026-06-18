# File Research: sources/os/linux/linux/fs/smb/client/cifsglob.h

## Purpose
`cifsglob.h` is the central shared state and contract header for the CIFS/SMB client. It defines global constants, mount/security flags, status enums, core server/session/tree/file/inode structures, the SMB dialect operation vtable, request/mid structures, lock-ordering documentation, global externs, and inline helpers.

## Major Constants and Enums
- Ports and path sizes:
  - `CIFS_PORT`, `RFC1001_PORT`, `SMB_PATH_MAX`, `MAX_TREE_SIZE`
- Request and credit limits:
  - `CIFS_MAX_REQ`
  - `SMB2_MAX_CREDITS_AVAILABLE`
  - `MAX_COMPOUND`
- Cache/time values:
  - `CIFS_DEF_ACTIMEO`
  - `CIFS_MAX_ACTIMEO`
  - echo interval bounds
- Status enums:
  - `enum statusEnum` for TCP connection state.
  - `enum ses_status_enum` for SMB session state.
  - `enum tid_status_enum` for tree connection state.
- Security/auth enums:
  - `enum securityEnum`
  - `enum upcall_target_enum`
- Reparse and symlink behavior enums:
  - `enum cifs_reparse_type`
  - `enum cifs_symlink_type`

## Core Structures
- `struct session_key`: response/session-key blob.
- `struct cifs_secmech`: SMB3 AEAD encryption/decryption transforms.
- `struct ntlmssp_auth`: NTLMSSP flags, challenge, and ciphertext.
- `struct cifs_open_info_data`: unified query/open metadata, reparse data, WSL EAs, symlink target, POSIX owner/group SIDs, and file info union.
- `struct smb_rqst`: SMB request kvecs plus data iterator/buffer.
- `struct smb_version_operations`: very large dialect vtable for SMB1/2/3 operations.
- `struct TCP_Server_Info`: per TCP/RDMA server connection state.
- `struct cifs_ses`: per SMB session/authentication state, including multichannel data.
- `struct cifs_tcon`: per tree/share connection state.
- `struct tcon_link`: refcounted per-user tcon link container.
- `struct cifs_fid`: protocol file id/lease key state.
- `struct cifsFileInfo`: per-open file state, locks, deferred close, oplock work, search info.
- `struct cifs_io_request` / `struct cifs_io_subrequest`: netfs IO request wrappers.
- `struct cifsInodeInfo`: CIFS inode extension embedding `struct netfs_inode`.
- `struct mid_q_entry`: pending multiplexed SMB request/response tracking entry.
- DFS, mount, channel, interface, lock, and compound-request helper structs.

## SMB Version Operation Vtable
`struct smb_version_operations` abstracts dialect-specific behavior. It includes hooks for:
- request setup/signing/cancel/receive/error mapping,
- credit accounting,
- negotiate/session/tree connect/disconnect,
- DFS referrals and server interface queries,
- path/file info query and mutation,
- open/close/flush/read/write/readdir,
- oplock/lease handling,
- server-side copy/clone,
- extended attributes and ACLs,
- encryption/compression transforms,
- reparse point handling,
- POSIX/special file creation,
- fiemap/llseek and status checks.

This vtable is the main indirection point that allows common VFS code to dispatch to SMB1, SMB2.1, SMB3.0, SMB3.02, or SMB3.1.1 behavior.

## Locking and Concurrency
The file contains a detailed lock-ordering table covering:
- mount/session/tcon/server locks,
- global MID/XID locks,
- server request/mid locks,
- session interface/channel locks,
- inode and file locks,
- cached directory locks,
- RDMA and MID callback locks.

This is important because CIFS combines VFS locks, network reconnect paths, oplock callbacks, deferred close work, and pending request completion.

## Inline Helpers
- Server locking with `memalloc_nofs_save()`:
  - `cifs_server_lock()`
  - `cifs_server_unlock()`
- Credit helpers:
  - `in_flight()`
  - `has_credits()`
  - `add_credits()`
  - `add_credits_and_wake_if()`
  - `set_credits()`
  - `adjust_credits()`
- MID helpers:
  - `get_next_mid64()`
  - `get_next_mid()`
  - `revert_current_mid()`
  - `mid_execute_callback()`
- Namespace/network helpers:
  - `cifs_net_ns()`
  - `cifs_set_net_ns()`
- Path and mount helpers:
  - `CIFS_SB()`
  - `cifs_sb_flags()`
  - `CIFS_DIR_SEP()`
  - `convert_delimiter()`
- DFS and error classification:
  - `is_tcon_dfs()`
  - `cifs_is_referral_server()`
  - `is_interrupt_error()`
  - `is_retryable_error()`
  - `is_replayable_error()`
- Cache/oplock helpers:
  - `CIFS_CACHE_READ()`
  - `CIFS_CACHE_HANDLE()`
  - `CIFS_CACHE_WRITE()`
  - `cifs_reset_oplock()`
- Reconnect scheduling:
  - `cifs_queue_server_reconn()`
  - `cifs_requeue_server_reconn()`
- File open options:
  - `cifs_open_create_options()`

## Global Externs
The header declares globals defined primarily by `cifsfs.c`, including:
- `cifs_tcp_ses_list`, `cifs_tcp_ses_lock`
- XID counters and `GlobalMid_Lock`
- allocation/reconnect/stat counters
- module parameters such as `enable_oplocks`, `global_secflags`, `CIFSMaxBufSize`, `cifs_max_pending`
- workqueues
- request/mid/netfs mempools
- dialect operation/value structs

## Role in the Group
This is the architectural backbone of the SMB client. `cifsfs.c`, `cifsacl.c`, and `cifsencrypt.c` all depend on its state definitions and helpers.
