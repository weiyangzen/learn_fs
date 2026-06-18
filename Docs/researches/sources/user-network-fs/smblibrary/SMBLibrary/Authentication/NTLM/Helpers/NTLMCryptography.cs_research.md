<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/NTLMCryptography.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/NTLMCryptography.cs

## Purpose
`NTLMCryptography` implements the LM/NTLM response, key derivation, signing, sealing, MIC, DES, RC4, MD4, MD5, and HMAC-MD5 primitives required by NTLM authentication.

## Important APIs and Types
Key APIs include `ComputeLMv1Response()`, `ComputeNTLMv1Response()`, `ComputeNTLMv1ExtendedSessionSecurityResponse()`, `ComputeLMv2Response()`, `ComputeNTLMv2Proof()`, `LMOWFv1()`, `NTOWFv1()`, `NTOWFv2()`, `KXKey()`, `ValidateAuthenticateMessageMIC()`, sign/seal key derivation, `ComputeMechListMIC()`, and `ComputeMessageSignature()`.

## Control Flow
v1 responses DESL-encrypt an 8-byte challenge with LM/NT hashes. Extended session security hashes server/client challenges with MD5 before DESL. v2 derives an HMAC-MD5 response key over uppercased user plus domain, then computes LMv2 or NT proof over server challenge and the client challenge structure. KXKEY follows flag-dependent MS-NLMP branches. Signing derives magic-constant keys, HMACs sequence number plus message, RC4-encrypts the first eight hash bytes, and prepends signature version.

## State, Dependencies, and Integration
The class is stateless except for caller-supplied `RC4KeyState` mutation during signing. Client and server NTLM providers both depend on it for authentication and session keys.

## Risks and Test Signals
Randomness is supplied by callers, often `Random`, not CSPRNG. DES weak-key support uses reflection into runtime internals. `ValidateAuthenticateMessageMIC()` mutates the supplied authenticate buffer by zeroing the MIC. Tests need MS-NLMP vectors for v1/v2/KXKEY/MIC/signature, weak DES keys, and MIC mutation awareness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/NTLMCryptography.cs -->
