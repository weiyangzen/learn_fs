# File Research: sources/os/linux/linux-stable/fs/ceph/crypto.c

## Purpose

`crypto.c` integrates CephFS with Linux fscrypt. It handles encryption context get/set, new-inode context preparation, encrypted filename conversion, snapshot-name special cases, readdir preparation, and page/block encryption/decryption helpers used by Ceph OSD I/O.

## fscrypt Operations

- `ceph_crypt_get_context()` reads the fscrypt auth blob from `ci->fscrypt_auth`, validates Ceph auth version, and copies the fscrypt context.
- `ceph_crypt_set_context()` wraps the fscrypt context in `ceph_fscrypt_auth` and persists it through `__ceph_setattr()`.
- `ceph_crypt_empty_dir()` treats a directory as empty when recursive subdirs plus files count is one.
- `ceph_get_dummy_policy()` returns the mount dummy encryption policy.
- `ceph_fscrypt_set_ops()` installs Ceph’s `fscrypt_operations` on the superblock.

## New Inode Encryption Context

`ceph_fscrypt_prepare_context()`:
- Calls `fscrypt_prepare_new_inode()`.
- Allocates and fills `ceph_fscrypt_auth` for encrypted new inodes.
- Stores a copy in `ci->fscrypt_auth`.
- Sets `S_ENCRYPTED` on the inode.

`ceph_fscrypt_as_ctx_to_req()` transfers prepared auth context into an MDS request.

## Encrypted Name Encoding

`ceph_encode_encrypted_dname()`:
- Handles special snapshot names beginning with `_`.
- Encrypts cleartext names with fscrypt when a key is available.
- Caps long ciphertext names by hashing the tail after `CEPH_NOHASH_NAME_MAX`.
- Base64-encodes ciphertext using `BASE64_IMAP`.
- Preserves special snapshot format by appending `_<inode-number>` when needed.

Special helper:
- `parse_longname()` parses synthetic snapshot names of the form `_<SNAPSHOT-NAME>_<INODE-NUMBER>` and resolves the referenced inode.

## User-Facing Name Decoding

`ceph_fname_to_usr()`:
- Validates name sizes.
- Handles special snapshot longnames.
- Returns raw names for unencrypted directories.
- Prepares encrypted readdir state.
- If no encryption key is available, returns the raw MDS-provided name and can mark `is_nokey`.
- Otherwise base64-decodes or uses supplied ciphertext, then calls `fscrypt_fname_disk_to_usr()`.
- Rebuilds special snapshot longname format after decryption when applicable.

## Readdir Preparation

`ceph_fscrypt_prepare_readdir()` wraps `__fscrypt_prepare_readdir()`:
- Returns 0 if directory is unencrypted or still locked.
- If loading a key unlocks the directory, it clears Ceph’s complete-directory cache state and returns 1.
- Returns negative errno on fscrypt errors.

## Block and Page Crypto

- `ceph_fscrypt_decrypt_block_inplace()` and `ceph_fscrypt_encrypt_block_inplace()` log and delegate to fscrypt block helpers.
- `ceph_fscrypt_decrypt_pages()` decrypts complete `CEPH_FSCRYPT_BLOCK_SIZE` blocks across a page array.
- `ceph_fscrypt_decrypt_extents()` decrypts sparse extents received from OSD reads, skipping holes and validating encryption-block alignment.
- `ceph_fscrypt_encrypt_pages()` encrypts complete crypto blocks across a page array.

All page-array helpers ignore partial trailing blocks by masking length to `CEPH_FSCRYPT_BLOCK_MASK`.

## Important Dependencies

- `crypto.h` for constants, structures, declarations, and inline helpers.
- `addr.c` for encrypted OSD read/write alignment, sparse extent decryption, and fscrypt bounce-page handling.
- `caps.c` for fscrypt auth encoding in cap messages and encrypted dentry release names.
- Linux fscrypt, base64, SHA-256, and Ceph striper/object mapping helpers.

## Edge Cases and Risks

- Snapshot longname parsing depends on the final underscore separating snapshot name and inode number.
- Very long encrypted filenames are lossy in the visible MDS name because the tail is SHA-256-hashed; full encrypted name preservation is handled elsewhere through dentry alternate names.
- Encrypted sparse extents must be block-aligned; misaligned extents return `-EIO`.
- Without a loaded key, user-facing conversion intentionally returns raw encoded MDS names rather than fscrypt nokey names.
