<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Enums/AuthenticationMethod.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/Enums/AuthenticationMethod.cs

## Purpose
`AuthenticationMethod` enumerates the NTLM variants supported by the client helpers.

## Important APIs and Types
Values are `NTLMv1`, `NTLMv1ExtendedSessionSecurity`, and `NTLMv2`.

## Control Flow
The enum has no behavior. Client code switches on it to set negotiate flags and compute the correct response and session keys.

## State, Dependencies, and Integration
`SMB1Client`, `NTLMAuthenticationClient`, and `NTLMAuthenticationHelper` accept this enum. The default login path uses NTLMv2.

## Risks and Test Signals
The enum does not include Kerberos or external SSPI modes. Tests should verify each value selects the expected flags/responses and that unsupported combinations, such as NTLMv1 extended session security without SMB extended security, throw or fail predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/Enums/AuthenticationMethod.cs -->
