# File Research: sources/os/linux/linux/fs/ceph/crypto.c

## Purpose
Implements CephFS integration with Linux fscrypt, including encryption context storage via MDS attributes, encrypted filename encoding/decoding, readdir preparation, and block/page encryption helpers for file data.

## Main Responsibilities
- Registers Ceph fscrypt operations.
- Gets/sets Ceph fscrypt auth context.
- Prepares fscrypt context for newly created encrypted inodes.
- Transfers fscrypt auth context into MDS requests.
- Encodes encrypted dentry names for MDS requests.
- Converts MDS filenames back to user-visible names.
- Handles special Ceph snapshot-name longname format.
- Encrypts/decrypts page arrays and sparse extents.

## fscrypt Operations
- `ceph_crypt_get_context()` validates `ci->fscrypt_auth`, checks Ceph fscrypt auth version, and copies the inner fscrypt blob.
- `ceph_crypt_set_context()` wraps a new fscrypt context in `ceph_fscrypt_auth` and sends it through `__ceph_setattr()`, then marks inode `S_ENCRYPTED`.
- `ceph_crypt_empty_dir()` treats a directory as empty when recursive subdir/file counts total one.
- `ceph_get_dummy_policy()` returns the mount dummy encryption policy.
- `ceph_fscrypt_set_ops()` installs `ceph_fscrypt_ops` on the superblock.
- `ceph_fscrypt_free_dummy_policy()` releases dummy policy state.

## New Inode Context
- `ceph_fscrypt_prepare_context()`:
  - calls `fscrypt_prepare_new_inode()`;
  - allocates a `ceph_fscrypt_auth`;
  - fills its fscrypt blob via `fscrypt_context_for_new_inode()`;
  - copies auth data into `ci->fscrypt_auth`;
  - marks the inode encrypted.
- `ceph_fscrypt_as_ctx_to_req()` moves auth context from ACL/security context into an MDS request.

## Filename Handling
- `parse_longname()` handles special snapshot names of form `_<SNAPSHOT-NAME>_<INODE-NUMBER>`, returning the inode for the embedded inode number and updating the clear snapshot-name length.
- `ceph_encode_encrypted_dname()`:
  - handles snapdir longnames;
  - exits unchanged when the relevant directory has no fscrypt key;
  - encrypts cleartext name with `fscrypt_fname_encrypt()`;
  - hashes ciphertext tail when longer than `CEPH_NOHASH_NAME_MAX`;
  - base64-encodes ciphertext with `BASE64_IMAP`;
  - appends `_<inode>` for parsed long snapshot names.
- `ceph_fname_to_usr()`:
  - handles long snapshot names;
  - passes through unencrypted names;
  - calls `ceph_fscrypt_prepare_readdir()` for encrypted dirs;
  - returns raw MDS name when the key is unavailable;
  - base64-decodes MDS names unless binary ciphertext is supplied;
  - calls `fscrypt_fname_disk_to_usr()`;
  - reconstructs long snapshot display names when needed.
- `ceph_fscrypt_prepare_readdir()` wraps `__fscrypt_prepare_readdir()` and clears directory-complete cache state when a key becomes newly available.

## File Data Crypto
- `ceph_fscrypt_decrypt_block_inplace()` and `ceph_fscrypt_encrypt_block_inplace()` are tracing wrappers over fscrypt block helpers.
- `ceph_fscrypt_decrypt_pages()` decrypts complete `CEPH_FSCRYPT_BLOCK_SIZE` blocks across a page array and ignores incomplete trailing blocks.
- `ceph_fscrypt_decrypt_extents()` decrypts sparse read extents, verifying each sparse extent is crypto-block aligned.
- `ceph_fscrypt_encrypt_pages()` encrypts complete blocks across a page array.

## Integration
- `addr.c` uses these helpers for encrypted netfs reads, sparse reads, writeback bounce-page handling, and encrypted page offsets.
- `caps.c` encodes/decodes fscrypt auth and true encrypted file size in cap messages.
- MDS request paths use encrypted dentry-name encoding.

## Risk Notes
- Long encrypted names are truncated by hashing ciphertext tail; full encrypted names must be preserved elsewhere when needed.
- Snapshot longname parsing depends on underscore delimiters and decimal inode suffixes.
- For encrypted files, wire I/O must be crypto-block aligned; sparse extent misalignment is treated as `-EIO`.
- `ceph_fscrypt_prepare_context()` allocates auth state before `fscrypt_context_for_new_inode()`; error callers must handle cleanup of `as->fscrypt_auth`.
