# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscrypt1.h

## Role

`gscrypt1.h` declares Adobe Type 1 encryption/decryption APIs and defines the state-update macros/constants.

This is font data encoding API infrastructure, not filesystem code.

## Public API

- `typedef ushort crypt_state`
- `gs_type1_encrypt`
- `gs_type1_decrypt`

## Main Macros And Constants

- `crypt_c1`
- `crypt_c2`
- `crypt_c1_inverse`
- `encrypt_next`
- `decrypt_this`
- `decrypt_next`
- `decrypt_skip_next`
- `decrypt_skip_previous`

## Core Behavior

Encryption and decryption use the standard 16-bit rolling Type 1 cipher state. The inverse constant supports stepping state backward with `decrypt_skip_previous`.

## Notable Risks

Macro arguments have side effects through state mutation; callers must avoid expressions with unintended repeated side effects.
