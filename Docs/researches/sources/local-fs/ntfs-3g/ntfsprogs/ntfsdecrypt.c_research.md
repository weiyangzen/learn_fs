# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdecrypt.c

## Role

Implements `ntfsdecrypt`, which decrypts EFS-encrypted NTFS file contents to stdout or encrypts replacement stdin data back into an already encrypted file while preserving the existing EFS key material.

## Main Areas

- CLI parsing selects keyfile, target file/inode, update/encrypt mode, force, and logging.
- Crypto initialization wires libgcrypt and GnuTLS.
- PKCS#12 loading reads a `.pfx/.p12` file, prompts for its passphrase, verifies MAC, extracts RSA private key parameters, detects EFS certificate purpose OID, and returns the certificate SHA-1 thumbprint.
- RSA FEK decryption reverses raw FEK bytes, converts to libgcrypt MPI/S-expression, decrypts with the private key, removes PKCS#1 padding, and imports the symmetric FEK.
- FEK import supports DESX, 3DES, and AES-256, with DES/unknown algorithms rejected.
- DESX support expands the Windows EFS DESX key using MD5 salts and implements sector encryption/decryption block-by-block.
- `ntfs_inode_fek_get()` reads `$LOGGED_UTILITY_STREAM:$EFS`, chooses DDF or DRF arrays based on certificate purpose, matches thumbprint credentials, and decrypts the matching FEK.
- `ntfs_cat_decrypt()` temporarily clears the encrypted flag and extends readable size to raw allocation so it can read encrypted sectors, decrypt 512-byte sectors, and emit only logical data size.
- `ntfs_feed_encrypt()` truncates the encrypted data stream, reads stdin in 512-byte sectors, pads the last sector with pseudo-random bytes, encrypts each sector, writes raw encrypted data, truncates to logical size, and updates timestamps.

## Dependencies

Uses libgcrypt, GnuTLS PKCS#12/X.509 APIs, and libntfs-3g volume, inode, attribute, directory/pathname, layout/EFS structure, logging, and utility APIs.

## Important Behavior

Decryption mode mounts read-only; encrypt/update mode mounts read-write unless force recovery is requested. Sector IVs are manually XORed because libgcrypt IV handling does not match the AES-256 EFS sector format used here.

The password buffer returned by `getpass()` is zeroed after key extraction. The FEK is decrypted in place within the `$EFS` buffer copy, not on disk.

## Research Notes

This file is crypto-sensitive and format-sensitive. It depends on exact EFS structure offsets, certificate thumbprint matching, RSA parameter conversion between GnuTLS and libgcrypt, and per-sector EFS IV constants.
