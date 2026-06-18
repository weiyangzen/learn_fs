<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.cs

## Purpose
`SSPIHelper.cs` contains shared Win32 SSPI interop declarations and common helpers for security context initialization and context attributes.

## Important APIs, Types, And Functions
It defines `SecHandle`, `MAX_TOKEN_SIZE`, SSPI status constants, credential/context flags, `SEC_WINNT_AUTH_IDENTITY`, `SecPkgContext_SessionKey`, and P/Invokes `AcquireCredentialsHandle`, `InitializeSecurityContext`, `AcceptSecurityContext`, `QueryContextAttributes`, `FreeContextBuffer`, `FreeCredentialsHandle`, and `DeleteSecurityContext`. Public helpers are `GetInitialMessage`, `GetUserName`, `GetSessionKey`, and `GetAccessToken`.

## Control Flow
`GetInitialMessage` initializes a client security context with confidentiality and integrity flags and returns the output token. Attribute helpers query context name, session key, or access token and return null/zero on failure. `GetWinNTAuthIdentity` packages domain/user/password strings and lengths for SSPI credential acquisition.

## State And Persistence
The file persists no managed state. It allocates output buffers per call and returns native handles or token bytes. Session key bytes are copied from native memory; access tokens remain native handles owned by the SSPI context/caller contract.

## Dependencies And Integration Points
It is the base partial class for NTLM and Kerberos helper files. Integrated authentication providers use it to create, authenticate, inspect, and delete SSPI contexts.

## Risks
`QueryContextAttributes` allocations for strings/session keys may require `FreeContextBuffer`, but `GetUserName` and `GetSessionKey` do not free returned native buffers. `GetWinNTAuthIdentity` uses ANSI flag despite .NET strings and will throw if strings are null. `GetInitialMessage` disposes buffers manually and could leak if an exception is thrown before disposal. Error handling is exception-based.

## Test Signals
No direct SSPI helper tests are present. Behavior is indirectly required for Windows integrated NTLM/Kerberos authentication.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.cs -->
