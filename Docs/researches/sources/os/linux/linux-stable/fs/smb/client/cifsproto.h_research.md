# File Research: sources/os/linux/linux-stable/fs/smb/client/cifsproto.h

Read status: complete.

## Purpose

Central prototype and inline-helper header for CIFS client implementation files. It declares buffer, transport, mount, session, inode, ACL, crypto, DFS, multichannel, reparse, lock, and utility functions implemented across the SMB client.

## Main Responsibilities

- Expose cross-file function prototypes.
- Provide XID tracing macros.
- Provide small inline wrappers for optional dialect operations and common helpers.
- Define helper functions for path allocation, session refcounting, MID refcounting, EIO tracing, scatterlist setup, and readable/writable open-file lookup.

## Major Prototype Groups

### Buffer and Transport

- CIFS large/small buffer allocation and release:
  - `cifs_buf_get()`
  - `cifs_buf_release()`
  - `cifs_small_buf_get()`
  - `cifs_small_buf_release()`
  - `free_rsp_buf()`

- Socket and send/receive paths:
  - `smb_send_kvec()`
  - `__smb_send_rqst()`
  - `cifs_call_async()`
  - `cifs_send_recv()`
  - `compound_send_recv()`
  - `wait_for_response()`
  - `wait_for_free_request()`
  - `cifs_wait_mtu_credits()`

- Receive helpers:
  - `cifs_read_from_socket()`
  - `cifs_discard_from_socket()`
  - `cifs_read_iter_from_socket()`
  - `cifs_readv_receive()`

### XID Tracing

- `get_xid()`
  - Wraps `_get_xid()`, logs current function and fsuid, and emits trace entry.

- `free_xid(curr_xid)`
  - Wraps `_free_xid()`, logs function exit and emits success/error trace based on local `rc`.

### Mount, Path, Session, and Reconnect

- Path construction and parsing:
  - `build_path_from_dentry()`
  - `cifs_build_path_to_root()`
  - `cifs_build_devname()`
  - `smb3_parse_devname()`
  - `smb3_fs_context_fullpath()`
  - `extract_unc_hostname()`
  - `extract_hostname()`
  - `extract_sharename()`

- Mount lifecycle:
  - `cifs_setup_cifs_sb()`
  - `cifs_mount()`
  - `cifs_umount()`
  - `cifs_match_super()`
  - mount session/tcon helper routines

- Session and reconnect:
  - `cifs_get_tcp_session()`
  - `cifs_put_tcp_session()`
  - `cifs_negotiate_protocol()`
  - `cifs_setup_session()`
  - `cifs_reconnect()`
  - reconnect marking helpers

### Inode and File Metadata

- Attribute conversion and inode population:
  - `cifs_fill_uniqueid()`
  - `cifs_unix_basic_to_fattr()`
  - `cifs_dir_info_to_fattr()`
  - `cifs_fattr_to_inode()`
  - `cifs_iget()`
  - `cifs_get_inode_info()`
  - `smb311_posix_get_inode_info()`
  - `cifs_get_inode_info_unix()`

- File state:
  - writable/readable open-file lookup
  - `cifs_new_fileinfo()`
  - `cifs_file_flush()`
  - `cifs_file_set_size()`
  - deferred close management

### ACL and Security Descriptor Operations

- ID/SID and ACL translation:
  - `sid_to_id()`
  - `cifs_acl_to_fattr()`
  - `id_mode_to_cifs_acl()`
  - `get_cifs_acl()`
  - `get_cifs_acl_by_fid()`
  - `set_cifs_acl()`
  - `cifs_get_acl()`
  - `cifs_set_acl()`

- ACE construction:
  - `setup_authusers_ACE()`
  - `setup_special_mode_ACE()`
  - `setup_special_user_owner_ACE()`

### Crypto and Authentication

- `setup_ntlmv2_rsp()`
- `calc_seckey()`
- `cifs_crypto_secmech_release()`
- `generate_smb30signingkey()`
- `generate_smb311signingkey()`
- `E_md4hash()`
- `__cifs_calc_signature()`
- `cifs_select_sectype()`

### Locks, Oplocks, and Deferred State

- Oplock and writer state:
  - `cifs_set_oplock_level()`
  - `cifs_get_writer()`
  - `cifs_put_writer()`
  - `cifs_done_oplock_break()`
  - `cifs_queue_oplock_break()`

- Byte-range locks:
  - `cifs_unlock_range()`
  - `cifs_push_mandatory_locks()`
  - `cifs_find_lock_conflict()`
  - lock list helpers

- Deferred and pending opens:
  - `cifs_add_pending_open()`
  - `cifs_del_pending_open()`
  - `cifs_is_deferred_close()`
  - deferred-close add/delete/close helpers

### DFS, Multichannel, Reparse, and Special Files

- DFS:
  - `parse_dfs_referrals()`
  - `get_dfs_path()` inline when DFS upcall is enabled
  - DFS super/prepath helpers

- Multichannel:
  - `cifs_try_adding_channels()`
  - `smb3_update_ses_channels()`
  - channel reconnect/interface helpers
  - `SMB3_request_interfaces()`

- Reparse and symlink/special files:
  - `parse_reparse_point()`
  - SFU node creation helpers
  - `wire_mode_to_posix()`
  - MF symlink helpers

### Inline Helpers

- `send_cancel()`
  - Calls dialect-specific cancel operation when present.

- `alloc_dentry_path()` / `free_dentry_path()`
  - Name-buffer allocation wrappers.

- `cifs_create_options()`
  - Adds backup intent when backup credentials are active.

- `cifs_put_smb_ses()` and `cifs_smb_ses_inc_refcount()`
  - Session refcount helpers.

- `dfs_src_pathname_equal()`
  - Case-insensitive path comparison treating `/` and `\` as equivalent.

- `smb_EIO()`, `smb_EIO1()`, `smb_EIO2()`
  - Traceable `-EIO` helpers.

- `cifs_get_num_sgs()` and `cifs_sg_set_buf()`
  - Scatterlist sizing/population helpers for encrypted SMB transform data.

- `cifs_get_writable_file()` / `find_readable_file()`
  - Inline wrappers normalizing open-file lookup flags.

## Role in the Subsystem

`cifsproto.h` is the shared declaration surface for the CIFS client. It prevents implementation files from needing to include many private module headers for every cross-file symbol and centralizes frequently used inline behavior.
