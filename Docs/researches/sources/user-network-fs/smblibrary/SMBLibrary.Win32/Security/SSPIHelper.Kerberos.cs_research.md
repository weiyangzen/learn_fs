<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.Kerberos.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.Kerberos.cs

## Purpose
`SSPIHelper.Kerberos.cs` adds Kerberos credential acquisition helpers to the shared SSPI helper.

## Important APIs, Types, And Functions
It exposes `AcquireKerberosCredentialsHandle(string serverPrincipalName)` and `AcquireKerberosCredentialsHandle(string serverPrincipalName, string domainName, string userName, string password)`, both funneled to a private nullable-auth overload.

## Control Flow
The credential method optionally marshals `SEC_WINNT_AUTH_IDENTITY`, calls `AcquireCredentialsHandle` with the provided server principal and package `"Kerberos"` for inbound/outbound credentials, frees the temporary auth structure, throws on non-`SEC_E_OK`, and returns a `SecHandle`.

## State And Persistence
Returned credential handles are native SSPI resources. The method itself persists no state and frees only the temporary auth buffer, not the returned credential.

## Dependencies And Integration Points
It depends on the partial `SSPIHelper` core definitions and secur32. It is available for Kerberos-capable GSS/SPNEGO integration even though this subset mainly tests NTLM.

## Risks
Callers must release returned credentials with the private `FreeCredentialsHandle` path where available; no public dispose wrapper is provided. Passing null domain/user/password through `GetWinNTAuthIdentity` can throw because it uses `.Length`, so the explicit-credential overload expects non-null strings.

## Test Signals
No tests in this subset cover Kerberos SSPI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/SSPIHelper.Kerberos.cs -->
