# sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptoLite_bf32.cc

## Purpose

`XrdCryptoLite_bf32.cc` implements the lightweight `bf32` algorithm: Blowfish CFB64 encryption with a CRC32 appended to plaintext for validation after decryption.

## Important APIs and Functions

`XrdCryptoLite_bf32::Encrypt()` validates buffer sizes, appends a network-byte-order CRC32 to the plaintext, encrypts with OpenSSL `EVP_bf_cfb64()` using a zero IV, and returns plaintext length plus four bytes. `Decrypt()` decrypts with the same cipher/zero IV, extracts and verifies the trailing CRC32, and returns decrypted data length or `-EPROTO`. `XrdCryptoLite_New_bf32()` constructs the object and, on OpenSSL 3, attempts to load the legacy provider after fetching a common default digest.

## Control Flow

Encryption uses a stack buffer for messages up to 4096 bytes and `malloc()` for larger plaintext plus CRC. Decryption requires `dstLen > sizeof(crc32)` and `dstLen >= srcLen`, decrypts the entire source, then validates the CRC over all but the trailing four bytes.

## State and Persistence Behavior

The implementation has no per-message persistent state. `XrdCryptoLite_New_bf32()` contains a static provider-loader object so OpenSSL provider loading runs once per process. The cipher IV is always all zeros, making encryption deterministic for the same key/plaintext.

## Dependencies and Integration Points

It depends on OpenSSL EVP/provider APIs, `XrdOucCRC`, byte-order helpers, and `XrdSysHeaders`. It is selected by `XrdCryptoLite::Create("bf32")`.

## Risks and Edge Cases

The code does not check `EVP_CIPHER_CTX_new()` or EVP call return values before use. A fixed zero IV and Blowfish are legacy choices and should not be treated as modern confidentiality protection. If OpenSSL 3 legacy provider loading fails, cipher initialization may fail silently. `EVP_DecryptFinal_ex()` writes to `dst` rather than `dst + wLen`, though CFB mode with padding disabled normally produces no final bytes.

## Test Signals

Tests should cover encrypt/decrypt round trips, CRC corruption detection, short destination rejection, large-message heap path, OpenSSL 3 provider availability, unsupported/invalid key lengths, and deterministic ciphertext behavior.
