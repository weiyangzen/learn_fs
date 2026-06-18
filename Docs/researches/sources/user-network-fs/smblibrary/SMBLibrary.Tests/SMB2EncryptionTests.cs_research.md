<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2EncryptionTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2EncryptionTests.cs

## Purpose
`SMB2EncryptionTests.cs` validates SMB 3.0 key derivation and transform encryption/decryption behavior using Microsoft SMB encryption sample vectors.

## Important APIs, Types, And Functions
The tests call `SMB2Cryptography.GenerateClientEncryptionKey`, `GenerateClientDecryptionKey`, `EncryptMessage`, `DecryptMessage`, and parse `SMB2TransformHeader`. They compare outputs with `ByteUtils.AreByteArraysEqual`.

## Control Flow
Key generation tests derive client encryption and decryption keys from a fixed session key for dialect `SMB300`. The encryption test encrypts a fixed SMB2 message with a fixed key, nonce, and session ID, then compares ciphertext. The decryption test parses a transformed packet, extracts the encrypted payload after `SMB2TransformHeader.Length`, decrypts it, and compares plaintext.

## State And Persistence
All cryptographic and packet data is in-memory.

## Dependencies And Integration Points
It depends on SMB2 cryptography, AES-CCM utilities, and transform-header parsing. It protects SMB3 encrypted transport behavior.

## Risks
The encryption test intentionally ignores signature validation because the sample associated data contains non-zero nonce padding. Tests cover SMB300 only, not SMB302/SMB311 key labels or AES-GCM. Tampered signature and invalid transform tests are absent.

## Test Signals
Strong positive signal for SMB300 key derivation, encryption ciphertext generation, and decryption of known transform packets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2EncryptionTests.cs -->
