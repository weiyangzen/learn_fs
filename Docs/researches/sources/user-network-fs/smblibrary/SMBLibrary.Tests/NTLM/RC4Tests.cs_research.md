<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/RC4Tests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/RC4Tests.cs

## Purpose
`RC4Tests.cs` validates the RC4 implementation used by NTLM key exchange against published ARCFOUR draft vectors and streaming state behavior.

## Important APIs, Types, And Functions
The tests exercise `Utilities.RC4.Encrypt`, `RC4.InitializeStateFromKey`, `RC4KeyState`, `ByteReader.ReadBytes`, `ByteUtils.Concatenate`, and `ByteUtils.AreByteArraysEqual`.

## Control Flow
Three vector tests encrypt fixed plaintext with fixed keys and compare ciphertext. The streaming test initializes key state once, encrypts the plaintext in two segments, concatenates the outputs, and compares to the single-vector expected ciphertext.

## State And Persistence
All state is in-memory. The streaming test specifically verifies mutable `RC4KeyState` continuity across calls.

## Dependencies And Integration Points
It depends on `Utilities.RC4` and utility byte helpers. It supports NTLM tests and production NTLM key exchange.

## Risks
RC4 is a legacy weak cipher, but still required for NTLM compatibility. Tests do not cover decryption separately, empty inputs, or key validation, and only one streaming segmentation pattern is checked.

## Test Signals
Good signal for RC4 keystream correctness and stateful continuation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/RC4Tests.cs -->
