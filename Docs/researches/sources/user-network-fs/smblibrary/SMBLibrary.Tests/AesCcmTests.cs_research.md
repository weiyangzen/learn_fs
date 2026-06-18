<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/AesCcmTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/AesCcmTests.cs

## Purpose
`AesCcmTests.cs` validates the utility AES-CCM implementation against RFC 3610 and SMB 3.0 encryption-oriented vectors.

## Important APIs, Types, And Functions
The MSTest class `AesCcmTests` calls `AesCcm.Encrypt` and `AesCcm.DecryptAndAuthenticate`, comparing ciphertext, plaintext, and authentication tags with `ByteUtils.AreByteArraysEqual`.

## Control Flow
Each test constructs static key, nonce, plaintext/ciphertext, associated data, and expected tag bytes. Encryption tests capture the calculated signature output parameter and compare both encrypted data and tag. Decryption tests pass ciphertext, associated data, and tag and compare the recovered plaintext.

## State And Persistence
The tests are pure in-memory cryptographic vector checks. They create no persistent state.

## Dependencies And Integration Points
They depend on `Utilities.AesCcm` and `Utilities.ByteUtils`. They protect lower-level cryptography used by SMB2/SMB3 message encryption.

## Risks
The tests cover known vectors but not invalid tag rejection, nonce length boundaries, empty payloads, large payloads, or parameter validation. The SMB vector comments reference archived Microsoft material, but the assertions are local byte fixtures.

## Test Signals
Strong signal for AES-CCM happy-path encryption/decryption compatibility. These tests complement `SMB2EncryptionTests`, which checks SMB transform/header integration around AES-CCM.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/AesCcmTests.cs -->
