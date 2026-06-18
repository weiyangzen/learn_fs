# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrypt1.c

## Role

`gscrypt1.c` implements Adobe Type 1 font encryption and decryption loops.

This is font data encoding infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_type1_encrypt`
- `gs_type1_decrypt`

## Core Behavior

Both functions copy the caller-provided crypt state locally, process `len` bytes, update output bytes using macros from `gscrypt1.h`, then write the final state back to `*pstate`.

Encryption processes each source byte through `encrypt_next`.

Decryption handles in-place source/destination overlap by first copying the input byte into a local `ch`, then applying `decrypt_next`.

## Dependencies

Uses basic Ghostscript types from `gstypes.h` and encryption macros from `gscrypt1.h`.

## Notable Risks

This is legacy Type 1 charstring/eexec-style obfuscation, not modern cryptography. It should not be used for security beyond compatibility with Adobe Type 1 formats.
