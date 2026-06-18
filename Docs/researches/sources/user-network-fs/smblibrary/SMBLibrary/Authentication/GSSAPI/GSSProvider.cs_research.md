<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/GSSProvider.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/GSSProvider.cs

## Purpose
`GSSProvider` is the server-side GSS/SPNEGO coordinator for SMB authentication. It advertises configured mechanisms, accepts SPNEGO `negTokenInit` / `negTokenResp` tokens, and also supports Windows-compatible raw NTLMSSP blobs in SMB security fields.

## Important APIs and Types
`GSSContext` stores the selected `IGSSMechanism` and its opaque mechanism context. `GSSProvider.GetSPNEGOTokenInitBytes()` emits a SPNEGO initial token containing every configured mechanism OID. `AcceptSecurityContext()` is the main state machine. `GetContextAttribute()`, `DeleteSecurityContext()`, `GetNTLMChallengeMessage()`, and `NTLMAuthenticate()` bridge downstream SMB server code to mechanism-specific auth state. `NTLMSSPIdentifier` is the NTLM OID.

## Control Flow
The acceptor first tries `SimpleProtectedNegotiationToken.ReadToken()`. For `negTokenInit`, it selects the preferred mechanism if available, otherwise the first supported mechanism from the offered list. Preferred mechanisms receive the embedded mechanism token immediately; fallback mechanisms return `SEC_I_CONTINUE_NEEDED` with a supported-mechanism response. `negTokenResp` messages require an existing context and forward `ResponseToken` to the selected mechanism. If SPNEGO parsing fails, a valid raw NTLMSSP signature is accepted and routed to the NTLM mechanism.

## State, Dependencies, and Integration
State is per-authentication context and delegated to the mechanism implementation. The provider depends on SPNEGO token classes, NTLM message utilities, `NTStatus`, and `ByteUtils`. SMB1/SMB2 session setup code can use this provider without knowing whether SPNEGO or raw NTLM carried the exchange.

## Risks and Test Signals
SPNEGO parser exceptions are swallowed before raw NTLM fallback, so malformed SPNEGO may be reported only as invalid token. Mechanism-list MIC is not validated here. Tests should cover preferred/fallback mechanism selection, raw NTLM negotiate/authenticate, null context response rejection, status-to-negState mapping, and legacy helper behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/GSSProvider.cs -->
