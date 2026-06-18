<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/NegotiateFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/NegotiateFlags.cs

## Purpose
`NegotiateFlags` defines NTLM negotiate capability and feature flags used across Type 1, Type 2, and Type 3 messages.

## Important APIs and Types
The `[Flags]` enum covers encoding, target-name request, signing/sealing, LAN Manager session key, NTLM session security, anonymous, supplied names, target type, extended session security, identify, non-NT session key, target info, version, 128-bit/56-bit encryption, and key exchange.

## Control Flow
The enum itself has no control flow. Providers and helpers combine bitmasks to choose authentication variants, key derivation, target-info presence, message version fields, and signing/sealing options.

## State, Dependencies, and Integration
Every NTLM message type and crypto branch depends on these constants. SMB1 session setup maps negotiated server capabilities and selected authentication method into these flags.

## Risks and Test Signals
Incorrect bit values silently break interoperability. Tests should assert all constants against MS-NLMP, verify mutually exclusive `LanManagerSessionKey`/`ExtendedSessionSecurity` handling, and cover flag propagation from negotiate to challenge to authenticate.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/NegotiateFlags.cs -->
