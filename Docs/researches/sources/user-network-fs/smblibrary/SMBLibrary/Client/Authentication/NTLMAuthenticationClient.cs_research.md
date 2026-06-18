<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/NTLMAuthenticationClient.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/NTLMAuthenticationClient.cs

## Purpose
`NTLMAuthenticationClient` implements client-side NTLM over raw SMB security blobs or SPNEGO/GSS wrapping.

## Important APIs and Types
Constructor captures domain, username, password, SPN, and `AuthenticationMethod`. `InitializeSecurityContext()` alternates between negotiate and authenticate phases. `GetSessionKey()` returns the NTLM session key. `ResetSecurityContext()` clears negotiation state for a new SPN.

## Control Flow
On first call, if the server supplied a security blob, it parses SPNEGO init/init2 and requires the NTLM OID. It creates an NTLM negotiate message and optionally wraps it in `negTokenInit`. On the second call, it parses a SPNEGO response when present, extracts the challenge, builds an authenticate message through `NTLMAuthenticationHelper`, stores the session key, and if wrapped, emits a `negTokenResp` containing the authenticate token and mech-list MIC.

## State, Dependencies, and Integration
State includes the previous negotiate bytes, session key, SPN, and a phase boolean. SMB1 extended session setup uses this class; DFS can reset it for referrals.

## Risks and Test Signals
It assumes a two-message NTLM exchange and returns null for unsupported SPNEGO mechanisms. MIC is computed over a one-entry NTLM mechanism list. Tests should cover raw mode, SPNEGO mode, unsupported mechanism rejection, reset, malformed challenge blobs, and session-key propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Authentication/NTLMAuthenticationClient.cs -->
