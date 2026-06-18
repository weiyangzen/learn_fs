<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2Cryptography.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2Cryptography.cs

Purpose: Internal SMB2/SMB3 cryptography helper for signing, key derivation, hashing, and AES-CCM message transforms.

Important APIs/types/functions: `CalculateSignature`, `VerifySignature`, signing/encryption/decryption key derivation methods, `TransformMessage`, `EncryptMessage`, `DecryptMessage`, and `ComputeHash` implement dialect-specific crypto behavior.

Control flow: Signing uses HMAC-SHA256 for SMB 2.0.2/2.1 and AES-CMAC for newer dialects, truncating to the 16-byte SMB2 signature. Key derivation uses SP800-108 labels/contexts, with SMB 3.1.1 requiring preauth hash input. Encryption builds an SMB2 transform header, derives associated data, AES-CCM encrypts, and prefixes the transform header.

State and persistence behavior: No persistence, but `VerifySignature` mutates the supplied message buffer by clearing its signature field. Nonces are generated per transform and embedded in the transform header.

Dependencies and integration points: Used by `SMB2Command.GetCommandChainBytes`, SMB3 session setup, signing verification, and encrypted transport paths. Depends on `System.Security.Cryptography`, `AesCmac`, `AesCcm`, `SP800_1008`, SMB2 dialect/transform enums, and utility byte helpers.

Risks and edge cases: `GenerateAesCcmNonce` uses `new Random()` rather than a cryptographic RNG, which is risky for encryption nonce uniqueness and unpredictability. `VerifySignature` mutates caller buffers; callers needing original bytes must copy first. Only SHA512 is supported in `ComputeHash`.

Test signals: Tests should use known-answer vectors for SMB2 HMAC/AES-CMAC signatures, SMB3 key derivation labels/contexts, AES-CCM transform round trips, signature verification mutation behavior, and SMB 3.1.1 null preauth-hash exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2Cryptography.cs -->
