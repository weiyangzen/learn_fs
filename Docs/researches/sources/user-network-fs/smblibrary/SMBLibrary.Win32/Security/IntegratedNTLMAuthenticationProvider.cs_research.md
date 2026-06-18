<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/IntegratedNTLMAuthenticationProvider.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/IntegratedNTLMAuthenticationProvider.cs

## Purpose
`IntegratedNTLMAuthenticationProvider.cs` implements an NTLM authentication provider backed by Windows SSPI and local account APIs, including guest fallback behavior that tries to mimic Windows server semantics.

## Important APIs, Types, And Functions
`IntegratedNTLMAuthenticationProvider : NTLMAuthenticationProviderBase` contains nested `AuthContext` with SSPI server context and decoded client identity fields. Key overrides are `GetChallengeMessage`, `Authenticate`, `DeleteSecurityContext`, and `GetContextAttribute`. Helpers include `EnableGuestLogin`, `IsUserExists`, and `ToNTStatus(Win32Error errorCode)`.

## Control Flow
Challenge creation calls `SSPIHelper.GetType2Message` from the client's negotiate bytes and stores the returned server context. Authentication parses `AuthenticateMessage`, populates context identity fields, handles anonymous or nonexistent users via optional guest login, then calls `SSPIHelper.AuthenticateType3Message`. Failed SSPI authentication can fall back to guest on `ERROR_ACCOUNT_RESTRICTION`; otherwise Win32 errors map to NT statuses. Context attributes expose access token, domain, guest flag, machine, OS version, session key, and user name.

## State And Persistence
Authentication state lives in `AuthContext` for a GSS/NTLM exchange. SSPI security contexts and access tokens are native OS resources. No persistent data is written.

## Dependencies And Integration Points
It depends on `SSPIHelper`, `NetworkAPI`, `LoginAPI`, `AuthenticateMessage`, `GSSAttributeName`, and SMBLibrary NTLM/GSS provider base classes. It integrates with SMB server session setup on Windows when OS-backed authentication is desired.

## Risks
Guest fallback is security-sensitive and depends on local policy and `Guest` account state. Exceptions from SSPI are collapsed to `SEC_E_INVALID_TOKEN`, which can hide operational causes. `EnableGuestLogin` calls `LogonUser` each time. Native access-token lifetime is delegated to callers. Nonexistent-user handling may allow guest when configured. Attribute `IsAnonymous` is not handled even though the enum contains it.

## Test Signals
No direct tests cover the integrated Windows provider in this subset. `LoginTests` use `IndependentNTLMAuthenticationProvider`, so this provider needs Windows-specific integration testing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/IntegratedNTLMAuthenticationProvider.cs -->
