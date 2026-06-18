<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NTLMAuthenticationHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NTLMAuthenticationHelper.cs

## Purpose
`NTLMAuthenticationHelper` builds client-side NTLM negotiate and authenticate messages, including session-key derivation and MIC calculation.

## Important APIs and Types
`GetNegotiateMessage()` has overloads for credential-based anonymous detection and explicit flags. `GetAuthenticateMessage()` parses the challenge, creates LM/NT responses for v1, v1 extended session security, or v2, derives the session key, encrypts it when key exchange is negotiated, calculates MIC, and returns an AUTHENTICATE_MESSAGE.

## Control Flow
Negotiate flags always request Unicode/OEM, signing, NTLM session security, target name, always-sign, version, and 128/56-bit encryption; non-anonymous requests key exchange. Authenticate parsing validates a Type 2 challenge, generates an 8-byte client challenge, mirrors server encoding/seal/key-exchange flags, branches on authentication method, constructs responses and key material, optionally encrypts a random session key, then computes MIC over negotiate/challenge/authenticate.

## State, Dependencies, and Integration
The helper is stateless but uses time, machine name, and random client challenges. `NTLMAuthenticationClient` and `SMB1Client` depend on it for extended-security NTLM.

## Risks and Test Signals
Random challenges/session keys use `Random`, not a CSPRNG. NTLMv2 LM response uses `challengeMessage.TargetName` as domain in one branch. Tests need MS-NLMP vectors for all methods, anonymous handling, key exchange, MIC validation, malformed challenge rejection, and SPN target-info insertion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Helpers/NTLMAuthenticationHelper.cs -->
