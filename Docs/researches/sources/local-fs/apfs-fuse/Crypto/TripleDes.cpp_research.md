# File Research: sources/local-fs/apfs-fuse/Crypto/TripleDes.cpp

## Role

`TripleDes.cpp` implements 3-key EDE Triple-DES and CBC mode by reusing the private DES primitive helpers.

## Core Behavior

- Constructor and destructor zero the three DES key schedules and IV.
- `SetKey()` reads three 8-byte DES keys from a 24-byte buffer and builds one schedule per key.
- `Encrypt()` performs DES encrypt with key 1, DES decrypt with key 2, and DES encrypt with key 3 for each block.
- `Decrypt()` performs the inverse D-E-D flow.
- `EncryptCBC()` XORs with `m_iv`, applies EDE encryption, and updates `m_iv`.
- `DecryptCBC()` stores ciphertext as next IV, applies inverse EDE, XORs with prior IV, and updates state.
- `SetIV()` sets or clears the 64-bit IV.

## Important Dependencies

- Depends on `Crypto/Des.h` and `Crypto/TripleDes.h`.
- Used by `ApfsLib/DiskImageFile.cpp` for encrypted disk-image compatibility.

## Notable Limitations And Risk Areas

- 3DES is legacy crypto and should only be used for compatibility.
- All encryption/decryption sizes must be multiples of 8; this is not checked.
- `SetKey()` assumes a valid 24-byte key buffer.
- CBC mode mutates IV state across calls.
