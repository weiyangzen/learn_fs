# File Research: sources/os/linux/linux/fs/smb/client/smbencrypt.c

## Purpose

`smbencrypt.c` provides the legacy NT password hash helper used by CIFS authentication code. Its active exported function, `E_md4hash()`, converts a password to NT Unicode and computes the MD4 hash.

## Main Behavior

- Defines small byte-order helper macros copied locally to avoid include conflicts.
- `mdfour()` wraps the CIFS MD4 implementation: initialize, update with input bytes, finalize into a 16-byte digest, and log failures.
- `E_md4hash()` converts a password to UTF-16 with `cifs_strtoUTF16()`, limits input to 128 characters, hashes the UTF-16 bytes with MD4, then wipes the stack password buffer with `memzero_explicit()`.

## Dependencies and Integration

- Includes CIFS Unicode, global, debug, and protocol headers.
- Uses `../common/md4.h` rather than the generic crypto API directly.
- Used by authentication paths that need the NT hash form of a password.

## Risk Notes

- MD4/NT hash handling is legacy and cryptographically weak, but required for compatibility with older SMB authentication mechanisms.
- The password conversion buffer is stack allocated and explicitly cleared; future changes should preserve sensitive-data wiping.
- The hash input length is based on UTF-16 character conversion count, not original byte length.
