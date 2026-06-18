<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMAuthenticationTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMAuthenticationTests.cs

## Purpose
`NTLMAuthenticationTests.cs` validates NTLM cryptographic primitives and message serialization against MS-NLMP-style known values.

## Important APIs, Types, And Functions
The tests exercise `NTLMCryptography.LMOWFv1`, `NTOWFv1`, `NTOWFv2`, `ComputeLMv1Response`, `ComputeNTLMv1Response`, `ComputeLMv2Response`, `ComputeNTLMv2Proof`, `ChallengeMessage`, `AuthenticateMessage`, `NTLMv2ClientChallenge`, `AVPairUtils`, `NTLMVersion`, and `NegotiateFlags`.

## Control Flow
Hash and response tests compute values from fixed password/user/domain/challenge inputs and compare with byte fixtures. Message tests build or parse challenge and authenticate messages, serialize them, and compare to expected byte layouts. The authenticate-message test reparses the expected bytes to normalize payload ordering before comparing serialized output.

## State And Persistence
All tests are pure in-memory byte-vector checks.

## Dependencies And Integration Points
They depend on `SMBLibrary.Authentication.NTLM` and `Utilities.ByteUtils`. They protect NTLM client/server authentication, exported session key derivation inputs, and higher-level SMB login behavior.

## Risks
The tests cover selected canonical vectors but not malformed messages, Unicode/OEM edge cases, target-info variants, channel binding, MIC presence in authenticate construction, or random challenge generation. LM/NTLMv1 vectors cover legacy algorithms that are security-sensitive despite being obsolete.

## Test Signals
Strong signal for core NTLM hash/response compatibility and basic challenge/authenticate message byte layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMAuthenticationTests.cs -->
