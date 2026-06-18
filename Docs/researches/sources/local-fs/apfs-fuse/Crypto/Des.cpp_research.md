# File Research: sources/local-fs/apfs-fuse/Crypto/Des.cpp

## Role

`Des.cpp` implements single-DES encryption/decryption and CBC mode. It is used as the base primitive for `TripleDES` and encrypted disk-image support.

## Core Behavior

- Constructor and destructor zero the key schedule and IV.
- `SetKey()` converts the 8-byte key to a 64-bit value, clears existing state, and computes 16 DES subkeys.
- `SetIV()` sets or clears the 64-bit CBC IV.
- `Encrypt()` and `Decrypt()` process 8-byte ECB blocks.
- `EncryptCBC()` XORs each plaintext block with the IV, encrypts it, and updates the IV to the ciphertext.
- `DecryptCBC()` preserves each ciphertext block as next IV, decrypts, then XORs with previous IV.
- Static helpers implement DES initial/final permutations, expansion, S-box substitution, P permutation, PC-1/PC-2 key scheduling, Feistel rounds, and big-endian byte conversion.

## Important Dependencies

- Implements `Crypto/Des.h`.
- `TripleDes.cpp` accesses private internals through friendship.
- Used by `ApfsLib/DiskImageFile.cpp` for legacy encrypted image handling.

## Notable Limitations And Risk Areas

- DES is cryptographically obsolete; this is compatibility code.
- ECB/CBC loops require `size` to be a multiple of 8 and do not validate it.
- No input/output pointer validation is performed.
- CBC methods mutate IV state, so repeated calls continue a stream unless callers reset the IV.
- Destructor clears key schedule with ordinary `memset`, which may not be guaranteed secure wiping.
