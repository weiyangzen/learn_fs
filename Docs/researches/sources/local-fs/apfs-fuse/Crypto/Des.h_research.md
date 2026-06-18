# File Research: sources/local-fs/apfs-fuse/Crypto/Des.h

## Role

`Des.h` declares the single-DES class and private DES primitive helpers.

## Public Interface

- `Encrypt()` and `Decrypt()` process block buffers.
- `EncryptCBC()` and `DecryptCBC()` process CBC buffers.
- `SetKey()` installs an 8-byte DES key.
- `SetIV()` installs or clears an 8-byte IV.

## Internal State

- `m_keySchedule[16]` stores the 16 DES subkeys.
- `m_initVector` stores CBC state.
- Static permutation, expansion, S-box, key-schedule, and byte-conversion helpers implement the algorithm.
- `TripleDES` is a friend so it can reuse the DES internals directly.

## Notable Limitations And Risk Areas

- The public API does not document block-alignment requirements.
- Raw-pointer calls make buffer-size correctness entirely a caller responsibility.
