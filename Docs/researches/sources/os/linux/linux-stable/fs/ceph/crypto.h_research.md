# File Research: sources/os/linux/linux-stable/fs/ceph/crypto.h

## Purpose

`crypto.h` declares CephFS fscrypt structures, constants, helpers, and disabled-build stubs. It is the shared interface between CephFS metadata/cap code, directory code, and address-space I/O for encrypted files.

## Main Definitions

- `CEPH_FSCRYPT_BLOCK_SHIFT`: 12.
- `CEPH_FSCRYPT_BLOCK_SIZE`: 4096-byte encryption block.
- `CEPH_FSCRYPT_BLOCK_MASK`: alignment mask for encryption-block boundaries.
- `struct ceph_fname`: MDS/raw/encrypted filename wrapper for user conversion.
- `struct ceph_fscrypt_truncate_size_header`: payload used when truncating encrypted files, including change attr, file offset, and block size.
- `struct ceph_fscrypt_auth`: Ceph wrapper around fscrypt context blob.
- `CEPH_FSCRYPT_AUTH_VERSION`: current auth wrapper version.
- `ceph_fscrypt_auth_len()`: computes encoded auth length.

## Enabled Build API

When `CONFIG_FS_ENCRYPTION` is enabled, the header declares:
- Superblock ops setup and dummy policy cleanup.
- New-inode context preparation and request transfer.
- Encrypted dentry-name encoding.
- Filename buffer allocation/free helpers.
- MDS-to-user filename conversion.
- Readdir preparation.
- Encryption-block counting and read alignment helpers.
- In-place block encrypt/decrypt wrappers.
- Page-array encrypt/decrypt helpers.
- Sparse extent decryption.
- Bounce-page to page-cache-page conversion.

Important inline helpers:
- `ceph_fscrypt_blocks(off, len)` counts 4096-byte crypto blocks covered by a range.
- `ceph_fscrypt_adjust_off_and_len()` expands encrypted reads to full crypto-block boundaries.
- `ceph_fscrypt_pagecache_page()` unwraps fscrypt bounce pages.
- `ceph_fscrypt_page_offset()` returns page-cache offset even for bounce pages.

## Disabled Build Behavior

When `CONFIG_FS_ENCRYPTION` is disabled:
- Most functions become no-ops or pass-through stubs.
- Preparing context under an encrypted directory returns `-EOPNOTSUPP`.
- Filename conversion returns the raw name.
- Crypto read/write alignment does nothing.
- Page encrypt/decrypt helpers return success without processing.
- Page-cache page helper returns the original page.

## Filename Length Design

The header documents Ceph’s encrypted filename strategy:
- Encrypted bytes are base64-encoded to avoid illegal filename characters.
- Base64 expansion can exceed `NAME_MAX`.
- Ceph limits the unhashed encrypted prefix to `CEPH_NOHASH_NAME_MAX`, then stores a SHA-256 tail hash.
- The 240-byte encoded target leaves space for synthetic snapshot names of the form `_<SNAPSHOT-NAME>_<INODE-NUMBER>`.

## Dependencies

- Linux fscrypt.
- Linux base64.
- SHA-256 definitions.
- Ceph MDS request, ACL/security context, and sparse extent types.
- Used by `crypto.c`, `addr.c`, and `caps.c`.
