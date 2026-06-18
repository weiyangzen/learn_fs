<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/Enums/GSSAttributeName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/Enums/GSSAttributeName.cs

## Purpose
`GSSAttributeName.cs` defines the attribute keys that SMBLibrary GSS mechanisms and authentication providers can expose after authentication.

## Important APIs, Types, And Functions
The enum `GSSAttributeName` contains `AccessToken`, `DomainName`, `IsAnonymous`, `IsGuest`, `MachineName`, `OSVersion`, `SessionKey`, and `UserName`. The `IsGuest` member documents guest-account fallback access.

## Control Flow
The file has no executable control flow. Providers switch on enum values to return context attributes.

## State And Persistence
No state is stored. The enum is an API contract.

## Dependencies And Integration Points
It is used by `IntegratedNTLMAuthenticationProvider.GetContextAttribute` and likely other GSS/NTLM mechanisms to expose identity, token, and session-key attributes to SMB server session handling.

## Risks
Adding or reordering enum values can affect binary consumers if values are serialized or persisted elsewhere. `IntegratedNTLMAuthenticationProvider` handles most values but not `IsAnonymous`, so consumers should expect null for unsupported attributes.

## Test Signals
No direct tests. `LoginTests` validate authentication success/failure but do not query GSS attributes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/GSSAPI/Enums/GSSAttributeName.cs -->
