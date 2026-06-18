# File Research: sources/local-fs/apfs-fuse/Crypto/TripleDes.h

## Role

`TripleDes.h` declares the 3-key Triple-DES class.

## Public Interface

- `Encrypt()` and `Decrypt()` process ECB-style block buffers.
- `EncryptCBC()` and `DecryptCBC()` process CBC buffers.
- `SetKey()` installs a 24-byte key.
- `SetIV()` installs or clears an 8-byte IV.

## Internal State

- `m_keySchedule[3][16]` stores three DES subkey schedules.
- `m_iv` stores CBC state.

## Notable Limitations And Risk Areas

- The API does not state required key length or 8-byte block alignment.
- Like DES, this is compatibility-oriented legacy crypto.
