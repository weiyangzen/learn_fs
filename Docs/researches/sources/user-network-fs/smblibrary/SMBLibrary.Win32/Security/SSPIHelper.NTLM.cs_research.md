<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.NTLM.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.NTLM.cs

## Purpose
`SSPIHelper.NTLM.cs` provides Windows SSPI NTLM credential acquisition and type 1/type 2/type 3 message helpers for client and server authentication.

## Important APIs, Types, And Functions
Public APIs include `AcquireNTLMCredentialsHandle`, `GetType1Message`, `GetType3Message`, `GetType2Message`, and `AuthenticateType3Message`. They use `SecHandle`, `SecBuffer`, `SecBufferDesc`, `AcquireCredentialsHandle`, `InitializeSecurityContext`, `AcceptSecurityContext`, and `FreeCredentialsHandle`.

## Control Flow
Credential acquisition optionally marshals explicit credentials, calls SSPI for package `"NTLM"`, frees the auth data, and returns a credential handle. Client type 1 creation acquires credentials, gets an initial security context token, then frees credentials. Type 3 creation feeds a type 2 token into `InitializeSecurityContext`. Server type 2 creation accepts a type 1 token with new inbound credentials. Authentication feeds the client's type 3 token into `AcceptSecurityContext` and returns true for `SEC_E_OK`, false for `SEC_E_LOGON_DENIED`, or throws for other SSPI errors.

## State And Persistence
Native client/server security contexts and credential handles are external resources. Buffers are allocated with unmanaged memory and disposed per call. The helper does not persist state itself.

## Dependencies And Integration Points
It depends on `SSPIHelper.cs`, `SecBuffer`, `SecBufferDesc`, and secur32. `IntegratedNTLMAuthenticationProvider` uses type 2 and type 3 server helpers. Client-side Windows authentication can use type 1/type 3 helpers.

## Risks
Credential and context ownership is manual. `GetType3Message` creates a `newContext` but returns only token bytes, leaving lifecycle expectations unclear. Explicit credential overloads can fail on null strings. Exceptions expose raw SSPI error codes rather than typed statuses except in the integrated provider wrapper.

## Test Signals
No direct tests use SSPI NTLM in this subset; NTLM cryptography tests cover the independent implementation, not Windows SSPI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.NTLM.cs -->
