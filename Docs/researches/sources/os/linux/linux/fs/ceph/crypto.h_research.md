# File Research: sources/os/linux/linux/fs/ceph/crypto.h

## Purpose
Declares CephFS fscrypt types, constants, and helpers, with full implementations when `CONFIG_FS_ENCRYPTION` is enabled and no-op/pass-through fallbacks otherwise.

## Key Types and Constants
- `CEPH_FSCRYPT_BLOCK_SHIFT = 12`
- `CEPH_FSCRYPT_BLOCK_SIZE = 4096`
- `CEPH_FSCRYPT_BLOCK_MASK`
- `struct ceph_fname`: carries MDS filename data, optional binary ciphertext, parent dir, lengths, and no-copy flag.
- `struct ceph_fscrypt_truncate_size_header`: metadata sent to MDS for encrypted truncate handling.
- `struct ceph_fscrypt_auth`: Ceph wrapper around fscrypt context blob.
- `CEPH_FSCRYPT_AUTH_VERSION = 1`
- `CEPH_NOHASH_NAME_MAX`: maximum ciphertext prefix kept before hashing long encrypted names.

## Main Interfaces With Encryption Enabled
- fscrypt setup:
  - `ceph_fscrypt_set_ops()`
  - `ceph_fscrypt_free_dummy_policy()`
  - `ceph_fscrypt_prepare_context()`
  - `ceph_fscrypt_as_ctx_to_req()`
- name handling:
  - `ceph_encode_encrypted_dname()`
  - `ceph_fname_alloc_buffer()`
  - `ceph_fname_free_buffer()`
  - `ceph_fname_to_usr()`
  - `ceph_fscrypt_prepare_readdir()`
- I/O alignment and crypto:
  - `ceph_fscrypt_blocks()`
  - `ceph_fscrypt_adjust_off_and_len()`
  - `ceph_fscrypt_decrypt_block_inplace()`
  - `ceph_fscrypt_encrypt_block_inplace()`
  - `ceph_fscrypt_decrypt_pages()`
  - `ceph_fscrypt_decrypt_extents()`
  - `ceph_fscrypt_encrypt_pages()`
  - `ceph_fscrypt_pagecache_page()`
  - `ceph_fscrypt_page_offset()`

## Fallback Behavior Without Encryption
- `ceph_fscrypt_prepare_context()` rejects encrypted parent dirs with `-EOPNOTSUPP`.
- Name conversion passes MDS names through unchanged.
- offset/length adjustment is a no-op.
- encrypt/decrypt helpers return success without transformation.
- `ceph_fscrypt_pagecache_page()` returns the original page.

## Important Inline Logic
- `ceph_fscrypt_auth_len()` returns wrapper header plus fscrypt blob length.
- `ceph_fscrypt_blocks()` computes the number of 4 KiB crypto blocks touched by an offset/length pair and asserts crypto blocks do not exceed page size.
- `ceph_fscrypt_adjust_off_and_len()` rounds encrypted reads down/up to full crypto blocks.
- `ceph_fscrypt_page_offset()` always resolves bounce pages back to their page-cache page before computing offset.

## Integration
- Used by address-space read/write code for block alignment and bounce-page handling.
- Used by cap message encoding/decoding for fscrypt auth and true file size.
- Used by dentry release and MDS request paths for encrypted names.

## Risk Notes
- The enabled and disabled configurations intentionally expose identical call sites but very different semantics.
- Correctness for encrypted I/O depends on all callers using adjusted offsets/lengths before OSD I/O.
- `ceph_fscrypt_page_offset()` is important for writeback code that may see fscrypt bounce pages.
