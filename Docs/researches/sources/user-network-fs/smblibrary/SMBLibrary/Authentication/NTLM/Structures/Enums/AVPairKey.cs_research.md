<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/AVPairKey.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/AVPairKey.cs

## Purpose
`AVPairKey` enumerates NTLM target-info AV pair keys used in challenge and client-challenge structures.

## Important APIs and Types
Values cover EOL, NetBIOS computer/domain names, DNS names, tree name, flags, timestamp, single-host data, target name, and channel bindings.

## Control Flow
The enum has no behavior. It drives `AVPairUtils`, `NTLMv2ClientChallenge`, MIC detection in `AuthenticateMessage`, and target-info creation in providers/helpers.

## State, Dependencies, and Integration
It is a protocol constant set shared throughout NTLM serialization/deserialization.

## Risks and Test Signals
`Flags` and `Timestamp` are both assigned `0x0006`; in MS-NLMP timestamp is normally a distinct key. This can cause timestamp AV pairs to be interpreted as flags and affects MIC detection. Tests should cover every assigned value against protocol constants, especially flags/timestamp behavior and unknown-key preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/Enums/AVPairKey.cs -->
