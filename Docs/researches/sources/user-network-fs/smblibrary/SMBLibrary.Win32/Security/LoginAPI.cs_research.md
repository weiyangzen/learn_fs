<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/LoginAPI.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/LoginAPI.cs

## Purpose
`LoginAPI.cs` wraps selected Windows logon APIs for credential validation, guest policy checks, and impersonation support.

## Important APIs, Types, And Functions
It defines `LogonType` values for interactive, network, and service logons. `LoginAPI` P/Invokes `advapi32!LogonUser`, `advapi32!ImpersonateLoggedOnUser`, and `kernel32!CloseHandle`. Public helpers are `ValidateUserPassword` and `HasEmptyPassword`.

## Control Flow
`ValidateUserPassword` calls `LogonUser` with an empty domain and provider `LOGON32_PROVIDER_WINNT40`, closes the returned token on success, returns false for expected account/logon denial errors, and throws on unexpected Win32 errors. `HasEmptyPassword` attempts network logon with an empty password and interprets success or selected policy errors as indicating empty-password behavior.

## State And Persistence
No persistent state is stored. Successful calls briefly acquire native token handles and close them.

## Dependencies And Integration Points
It depends on Win32 advapi32/kernel32 and `Utilities.Win32Error`. `IntegratedNTLMAuthenticationProvider` uses it to decide whether guest login is enabled.

## Risks
Unexpected errors throw exceptions, so callers must isolate OS/policy issues. Passing an empty domain restricts behavior to local/default context. Correct token cleanup is important; `ImpersonateLoggedOnUser` is exposed but no helper reverts impersonation.

## Test Signals
No direct tests in this subset. Behavior requires Windows account-policy integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/Security/LoginAPI.cs -->
