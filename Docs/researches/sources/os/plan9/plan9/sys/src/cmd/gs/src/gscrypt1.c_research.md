# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrypt1.c

## Purpose
Implements Adobe Type 1 encryption and decryption loops.

## Key Behavior
- `gs_type1_encrypt` encrypts a byte string using `encrypt_next` and updates the caller’s crypt state.
- `gs_type1_decrypt` decrypts a byte string using `decrypt_next` and updates the caller’s crypt state.

## Important Details
- Decryption stores the input byte in a temporary before writing output, allowing in-place decryption when `src == dest`.
- The actual cipher step macros and constants are in `gscrypt1.h`.

## Dependencies
Uses Ghostscript byte/uint types and Type 1 crypt macros.

## Research Notes
This is small font-encryption support code, not general-purpose cryptography.
