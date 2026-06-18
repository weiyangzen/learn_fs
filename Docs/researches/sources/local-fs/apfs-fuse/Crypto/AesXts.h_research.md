# File Research: sources/local-fs/apfs-fuse/Crypto/AesXts.h

## Role

`AesXts.h` declares the `AesXts` wrapper class around two `AES` instances for XTS-mode block encryption.

## Public Interface

- `CleanUp()` clears both AES contexts.
- `SetKey(key1, key2)` installs the data and tweak keys.
- `Encrypt(cipher, plain, size, unit_no)` encrypts a data unit.
- `Decrypt(plain, cipher, size, unit_no)` decrypts a data unit.

## Internal State

- `m_aes_1` performs data-block encryption/decryption.
- `m_aes_2` encrypts unit numbers into initial tweaks.
- Private helpers perform 128-bit XOR and tweak multiplication.

## Notable Limitations And Risk Areas

- The header does not document that sizes must be 16-byte aligned.
- The class is state-light after key setup, but not explicitly thread-safe because the embedded AES objects are mutable.
