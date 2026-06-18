# sources/user-network-fs/smblibrary/Utilities/Cryptography/AesCcm.cs

Purpose: `AesCcm` implements Counter with CBC-MAC mode as described by RFC 3610.

Important APIs/types/functions: public `Encrypt(key, nonce, data, associatedData, signatureLength, out signature)` and `DecryptAndAuthenticate(key, nonce, encryptedData, associatedData, signature)`; private `CalculateMac`, `BuildKeyStream`, `BuildB0Block`, `BuildABlock`, `ComputeFlagsByte`, and `AesEncrypt`.

Control flow: encryption validates nonce/tag length, builds an AES-CTR keystream, calculates CBC-MAC over B0, encoded associated data, padded associated data, and padded plaintext, XORs S0 with the MAC for the signature, then XORs plaintext with keystream after the first block. Decryption builds the same keystream, decrypts ciphertext, recomputes MAC, compares signatures, and throws on mismatch.

State and persistence behavior: stateless; all cryptographic material is passed as arrays and remains caller-managed.

Dependencies and integration points: uses `RijndaelManaged`, `CipherMode.CBC/ECB`, `ByteUtils`, `ByteReader`, `ByteWriter`, and `BigEndianConverter`. It likely supports SMB3 encryption/authentication paths.

Risks: associated data length >= 65280 is unsupported. Signature comparison uses non-constant-time `AreByteArraysEqual`. `RijndaelManaged` is legacy in modern .NET. Nonce reuse with a key would be catastrophic and is not prevented. Input arrays are not zeroed.

Test signals: RFC 3610 known-answer vectors, invalid nonce/tag length tests, tampered ciphertext/tag tests, empty associated data, unsupported associated-data length, and interop with platform AES-CCM where available.
