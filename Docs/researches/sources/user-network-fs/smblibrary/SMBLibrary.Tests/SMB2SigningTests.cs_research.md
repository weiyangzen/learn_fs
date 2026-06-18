<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2SigningTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2SigningTests.cs

## Purpose
`SMB2SigningTests.cs` validates SMB2/SMB3 message signature calculation for dialects SMB 2.0.2, SMB 2.1, and SMB 3.0.

## Important APIs, Types, And Functions
The tests use `SMB2Cryptography.CalculateSignature`, `SMB2Cryptography.GenerateSigningKey`, `SMB2Dialect.SMB202`, `SMB210`, `SMB300`, `ByteWriter.WriteBytes`, and `ByteUtils.AreByteArraysEqual`.

## Control Flow
Each test builds a fixed SMB2 message with an existing signature field, zeros the 16-byte signature at offset 48, calculates a signature using the dialect-specific algorithm/key, and compares against the expected signature bytes. The SMB300 test first derives a signing key from the exported session key.

## State And Persistence
All state is in-memory packet data and keys.

## Dependencies And Integration Points
It depends on SMB2 cryptography and byte utilities. The covered functionality is central to SMB session integrity when signing is enabled.

## Risks
Coverage stops at SMB300 and does not include SMB311 preauth-integrity-derived signing keys. It does not test verification failure, compound messages, or signing across partial buffers beyond full-message input.

## Test Signals
Strong signal for dialect-specific signing compatibility across SMB202/SMB210 HMAC-MD5 and SMB300 AES-CMAC style paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/SMB2SigningTests.cs -->
