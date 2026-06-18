<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/IndependentNTLMAuthenticationProvider.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/IndependentNTLMAuthenticationProvider.cs

## Purpose
`IndependentNTLMAuthenticationProvider` is a standalone server-side NTLM `IGSSMechanism` that validates challenge responses against a password lookup delegate.

## Important APIs and Types
`GetUserPassword` supplies passwords or null for missing accounts. `AuthContext` stores server challenge, negotiated identity, workstation, OS version, session key, and guest flag. `GetChallengeMessage()`, `CreateChallengeMessage()`, `Authenticate()`, `DeleteSecurityContext()`, and `GetContextAttribute()` implement mechanism behavior.

## Control Flow
On negotiate, it parses `NegotiateMessage`, generates an 8-byte server challenge, creates `AuthContext`, and returns a challenge with flags derived from the client request. On authenticate, it parses `AuthenticateMessage`, records identity fields, handles anonymous/guest login, checks `LoginCounter`, fetches the password, and validates v1, v1 extended-session-security, or v2 responses. Successful authentication derives the session key, decrypting `EncryptedRandomSessionKey` when key exchange is negotiated.

## State, Dependencies, and Integration
Per-context state lives in `AuthContext`; cross-context failed-attempt state lives in `LoginCounter`. It integrates with `GSSProvider` via `NTLMAuthenticationProviderBase`, and exposes GSS attributes for SMB sessions.

## Risks and Test Signals
`GenerateServerChallenge()` uses `Random`, not a cryptographic RNG. Guest login is enabled by a `Guest` password equal to empty string. MIC validation is not performed. Tests should cover invalid message parsing, lockout boundaries, guest/anonymous policy, v1/v2 success/failure, key exchange, and GSS attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/IndependentNTLMAuthenticationProvider.cs -->
