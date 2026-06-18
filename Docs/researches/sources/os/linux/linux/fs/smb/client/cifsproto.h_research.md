# File Research: sources/os/linux/linux/fs/smb/client/cifsproto.h

## Purpose
`cifsproto.h` declares the CIFS/SMB client function surface shared across implementation files. It also defines common small inline wrappers for XID tracing, dentry path allocation, cancel dispatch, DFS stubs, session refcounting, scatterlist setup, and EIO tracing.

## Major Prototype Areas
- Buffer management:
  - `cifs_buf_get()`, `cifs_buf_release()`
  - `cifs_small_buf_get()`, `cifs_small_buf_release()`
  - `free_rsp_buf()`
- XID accounting:
  - `_get_xid()`, `_free_xid()`
  - `get_xid()` and `free_xid()` trace/debug macros
- Path construction:
  - `build_path_from_dentry()`
  - `cifs_build_path_to_root()`
  - `cifs_build_devname()`
  - `smb3_fs_context_fullpath()`
  - UNC hostname/share extraction helpers
- Transport and MID handling:
  - `smb_send_kvec()`
  - `cifs_call_async()`
  - `cifs_send_recv()`
  - `compound_send_recv()`
  - `wait_for_response()`
  - `delete_mid()`, `dequeue_mid()`, `release_mid()`
- Reconnect/session/tcon:
  - `cifs_get_tcp_session()`
  - `cifs_put_tcp_session()`
  - `cifs_get_smb_ses()`
  - `cifs_tree_connect()`
  - `cifs_mount()`, `cifs_umount()`
  - multichannel functions
- Inode/file operations:
  - writable/readable file lookup,
  - inode info conversion,
  - file size and attr mutation,
  - locks and mandatory locks,
  - deferred close helpers,
  - deleted-file handle marking.
- ACL and idmap:
  - `sid_to_id()`
  - `cifs_acl_to_fattr()`
  - `id_mode_to_cifs_acl()`
  - `get_cifs_acl()`
  - `cifs_get_acl()`, `cifs_set_acl()`
  - special ACE setup helpers.
- Crypto/auth:
  - `setup_ntlmv2_rsp()`
  - `calc_seckey()`
  - `__cifs_calc_signature()`
  - SMB3 signing-key generation.
- DFS/reparse/symlink/special files:
  - DFS referral parsing and lookup stubs,
  - reparse point parsing,
  - SFU node creation,
  - MF symlink helpers.
- SMB3 transform helpers:
  - scatterlist sizing and buffer setup for encryption/decryption.

## Important Inline Helpers
- `alloc_dentry_path()` / `free_dentry_path()`: allocate/free path buffer using name cache.
- `send_cancel()`: optional dialect hook wrapper.
- `cifs_create_options()`: adds backup intent when backup credentials are in use.
- `cifs_put_smb_ses()` / `cifs_smb_ses_inc_refcount()`: SMB session refcount helpers.
- `dfs_src_pathname_equal()`: case-insensitive path comparison treating `/` and `\` as equivalent.
- `cifs_free_open_info()`: releases symlink/reparse resources and zeros open info.
- `smb_EIO()`, `smb_EIO1()`, `smb_EIO2()`: trace an SMB EIO cause and return `-EIO`.
- `cifs_get_num_sgs()`: computes scatterlist entry count for transformed requests.
- `cifs_sg_set_buf()`: scatterlist setup supporting vmalloc/module/stack-backed buffers.
- `cifs_get_writable_file()` and `find_readable_file()`: wrappers that normalize find flags.

## Role in the Group
This is the declaration hub connecting the implementation in `cifsfs.c`, ACL handling in `cifsacl.c`, crypto in `cifsencrypt.c`, transport/session code elsewhere, and dialect-specific SMB2/SMB3 modules.
