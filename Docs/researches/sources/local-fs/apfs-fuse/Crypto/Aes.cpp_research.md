# File Research: sources/local-fs/apfs-fuse/Crypto/Aes.cpp

## Role

`Aes.cpp` implements the `AES` class declared in `Aes.h`. It is a standalone, table-driven software AES implementation used by APFS encryption and wrapper crypto code in this source tree.

## Core Behavior

- Defines AES encryption tables `Te0` through `Te4`, decryption tables `Td0` through `Td4`, round constants `rcon`, and a zero IV buffer.
- Initializes AES state to AES-128 defaults in the constructor: `Nb = 4`, `Nk = 4`, `Nr = 10`, zero round keys, zero IV, and `_tp = 0`.
- `CleanUp()` zeros the IV, encryption round keys, decryption round keys, and CFB/OFB byte counter.
- `SetKey()` supports AES-128, AES-192, and AES-256 by selecting `Nk` and `Nr`, expanding `_erk`, deriving reversed/inverse `_drk`, and resetting the IV to zero.
- `Encrypt()` and `Decrypt()` operate on exactly one 16-byte block using the precomputed round keys and T tables.
- `EncryptCBC()` and `DecryptCBC()` process 16-byte blocks and mutate `_iv` to the last ciphertext block.
- `EncryptCFB()`, `DecryptCFB()`, and `CryptOFB()` are byte-stream modes that mutate both `_iv` and `_tp`.

## Important Dependencies

- Implements the interface in `Crypto/Aes.h`.
- Used by `Crypto/AesXts.cpp` and `Crypto/Crypto.cpp`.
- Indirectly supports APFS volume encryption through `ApfsLib/ApfsVolume` and key-management code.

## Notable Limitations And Risk Areas

- This is table-based AES with key-dependent memory accesses, so it is not constant-time.
- Public methods do not validate null pointers or buffer sizes.
- CBC callers must provide a byte count that is a multiple of 16; the implementation does not enforce that and will read/write past the requested logical end otherwise.
- `SetKey()` resets the IV, and all chaining modes mutate object state; callers must reset IVs explicitly when reusing an instance.
- `CleanUp()` uses ordinary `std::fill_n`; compilers may optimize sensitive-memory clearing in some contexts.
