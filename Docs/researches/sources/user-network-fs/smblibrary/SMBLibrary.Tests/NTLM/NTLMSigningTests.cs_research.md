<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMSigningTests.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMSigningTests.cs

## Purpose
`NTLMSigningTests.cs` validates NTLM message integrity code calculation, exported session key derivation helpers, NTLM signing/sealing key generation, and SPNEGO mechListMIC calculation.

## Important APIs, Types, And Functions
The class calls `NTLMCryptography.ValidateAuthenticateMessageMIC`, `ComputeClientSignKey`, `ComputeClientSealKey`, `ComputeMechListMIC`, `KXKey`, `NTOWFv1`, `NTOWFv2`, `AuthenticationMessageUtils.IsNTLMv2NTResponse`, `RC4.Decrypt`, `ChallengeMessage`, `AuthenticateMessage`, `MD4`, and `HMACMD5`. The private `GetExportedSessionKey` mirrors protocol key-selection logic.

## Control Flow
MIC tests parse captured type 1, type 2, and type 3 messages, derive session base and exported session keys according to NTLMv1, LM, extended session security, or NTLMv2 rules, then validate the authenticate MIC. Key tests compare deterministic sign/seal/mechListMIC outputs against fixed byte arrays.

## State And Persistence
The tests operate only on static in-memory byte arrays and derived keys.

## Dependencies And Integration Points
They depend on NTLM cryptography classes, RC4, MD4/HMAC-MD5 utilities, and message parsers. They protect SMB session signing and SPNEGO MIC behavior after authentication.

## Risks
Fixtures are large and brittle; a legitimate serializer layout change may require care to preserve MIC semantics. The private exported-key helper duplicates production logic and could mask shared misunderstandings. Negative MIC tests and tampered-message cases are absent.

## Test Signals
Strong compatibility signal for MIC validation across LM/NTLMv1/NTLMv1 ESS/NTLMv2 key-exchange paths and for derived client sign/seal keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Tests/NTLM/NTLMSigningTests.cs -->
