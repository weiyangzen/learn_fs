<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/MessageTypeName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/MessageTypeName.cs

## Purpose
`MessageTypeName` enumerates NTLMSSP message type numbers.

## Important APIs and Types
`Negotiate = 0x01`, `Challenge = 0x02`, and `Authenticate = 0x03` match Type 1, Type 2, and Type 3 NTLM messages.

## Control Flow
The enum has no behavior; parsers cast the little-endian 32-bit type field to this enum and dispatch accordingly.

## State, Dependencies, and Integration
`AuthenticationMessageUtils.GetMessageType()`, `NTLMAuthenticationProviderBase`, and the three message structures depend on these constants.

## Risks and Test Signals
Unknown values are representable by casts and must be rejected by dispatching code. Tests should verify wire values, invalid-type rejection in provider base, and structure constructors setting the expected message type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/MessageTypeName.cs -->
