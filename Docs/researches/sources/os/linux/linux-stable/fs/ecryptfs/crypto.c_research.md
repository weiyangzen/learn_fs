# File Research: sources/os/linux/linux-stable/fs/ecryptfs/crypto.c

## Summary
Implements eCryptfs cryptographic data handling: per-file crypto context setup, page/extent encryption and decryption, header and xattr metadata read/write, cipher code mapping, cached key transform management, and encrypted filename encode/decode support.

## Main Responsibilities
- Initialize and destroy per-inode `ecryptfs_crypt_stat` and mount-wide crypt state.
- Derive root IVs from file encryption keys and per-extent IVs from root IV plus extent offset.
- Encrypt and decrypt page contents one extent at a time using Linux Crypto API `skcipher` transforms.
- Read and write eCryptfs metadata from lower file headers or `user.ecryptfs` xattrs.
- Generate new file encryption keys and propagate mount-wide policy flags/signatures into inode crypt state.
- Validate eCryptfs file markers, parse/write file flags, and handle legacy version-0 header defaults.
- Map RFC2440 cipher codes to kernel cipher names and AES key sizes.
- Maintain a module-wide cache of key-encryption cipher transforms.
- Encrypt, encode, decode, and decrypt lower filenames using tag-70 FNEK packets and portable filename characters.
- Compute the effective encrypted-name maximum accepted through `ecryptfs_set_f_namelen()`.

## Key APIs
- `ecryptfs_new_file_context()`: creates a new encrypted file context, copies mount signatures, generates a FEK, and initializes the cipher.
- `ecryptfs_encrypt_page()` / `ecryptfs_decrypt_page()`: translate upper folios to lower encrypted page data.
- `ecryptfs_write_metadata()` / `ecryptfs_read_metadata()`: write or discover eCryptfs metadata in file contents or xattrs.
- `ecryptfs_read_and_validate_header_region()` / `ecryptfs_read_and_validate_xattr_region()`: lightweight marker checks and `i_size` initialization.
- `ecryptfs_encrypt_and_encode_filename()` / `ecryptfs_decode_and_decrypt_filename()`: dentry-name translation for filename encryption.
- `ecryptfs_get_tfm_and_mutex_for_cipher_name()`: shared transform lookup/creation for key and filename crypto.

## Important Behavior
Data encryption uses CBC-mode transforms named as `cbc(<cipher>)`, with the file FEK set lazily on the per-inode transform. Each page is split into `crypt_stat->extent_size` extents, and IVs are MD5-derived from the root IV and extent number.

Metadata layout starts with an unencrypted file-size field, an 8-byte randomized eCryptfs marker pair, flags/version, header extent metadata, and an authentication-token packet set. If xattr metadata is enabled, the lower file data starts at offset zero; otherwise `metadata_size` is reserved at the front of the lower file.

Filename encryption is only implemented for mount-wide FNEK mode in this file. It delegates packet construction/parsing to `keystore.c`, then applies a custom 6-bit portable alphabet and the `ECRYPTFS_FNEK_ENCRYPTED.` prefix for lower dentry names.

## Research Notes
This file is the central bridge between VFS/page-cache operations and eCryptfs' on-disk crypto format. Correctness depends on metadata location flags, extent-size calculations, matching cipher/key-size negotiation, and key availability before any encrypted file or filename path is processed.
