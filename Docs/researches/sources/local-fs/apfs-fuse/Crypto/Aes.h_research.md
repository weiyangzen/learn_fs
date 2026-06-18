# File Research: sources/local-fs/apfs-fuse/Crypto/Aes.h

## Role

`Aes.h` declares the repository's standalone AES class. It exposes block AES plus ECB-style single-block calls and CBC, CFB, and OFB stateful modes.

## Public Interface

- `Mode` selects key size: `AES_128`, `AES_192`, or `AES_256`.
- `CleanUp()` clears stored key material and IV state.
- `SetKey()` installs a key and resets the IV to zero.
- `SetIV()` installs an IV or a zero vector.
- `Encrypt()` and `Decrypt()` process a single 16-byte block.
- `EncryptCBC()` and `DecryptCBC()` process block-aligned buffers.
- `EncryptCFB()`, `DecryptCFB()`, and `CryptOFB()` process arbitrary byte counts with internal stream position state.

## Internal State

- `_erk[60]` and `_drk[60]` hold expanded round keys for AES-256 maximum schedule size.
- `_iv[16]` stores current chaining-mode state.
- `_tp` stores CFB/OFB byte position.
- `Nk`, `Nr`, and `Nb` store AES mode parameters.
- Static table declarations back the T-table implementation in `Aes.cpp`.

## Notable Limitations And Risk Areas

- The header documents block-size constraints but the class does not encode them in types.
- The class is mutable and not thread-safe if one instance is shared across operations.
- The API does not distinguish one-shot from streaming use, so callers must manage IV lifecycle carefully.
