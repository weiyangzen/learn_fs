# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscrypt1.h

## Purpose
Public interface and macro implementation for Adobe Type 1 encryption/decryption.

## Key Contents
- Defines `crypt_state` as `ushort`.
- Declares `gs_type1_encrypt` and `gs_type1_decrypt`.
- Defines Type 1 cipher constants:
  - `crypt_c1 = 52845`,
  - `crypt_c2 = 22719`,
  - `crypt_c1_inverse = 27493`.
- Defines encryption/decryption macros:
  - `encrypt_next`,
  - `decrypt_this`,
  - `decrypt_next`,
  - `decrypt_skip_next`,
  - `decrypt_skip_previous`.

## Important Details
- `decrypt_skip_previous` uses the modular inverse to rewind state.

## Research Notes
Implementation of bulk string processing is in `gscrypt1.c`.
