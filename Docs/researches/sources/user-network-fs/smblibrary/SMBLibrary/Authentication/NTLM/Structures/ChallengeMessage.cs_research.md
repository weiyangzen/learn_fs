<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/ChallengeMessage.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/ChallengeMessage.cs

## Purpose
`ChallengeMessage` models the NTLM Type 2 CHALLENGE_MESSAGE used by servers to send negotiate flags, target name, server challenge, target info, and optional version.

## Important APIs and Types
Fields include `TargetName`, `NegotiateFlags`, `ServerChallenge`, `TargetInfo`, and `Version`. The constructor parses a byte buffer; `GetBytes()` serializes fixed fields plus variable target-name and target-info payloads.

## Control Flow
Parsing reads the NTLM signature/type, target-name security buffer, flags, 8-byte server challenge, target-info buffer, and optional version at offset 48 when the flag is set. Serialization chooses fixed length 48 or 56, writes signature/type/flags/challenge/version, serializes AV pairs, then writes target name and target info through buffer pointers.

## State, Dependencies, and Integration
Server-side providers create challenges; client-side `NTLMAuthenticationHelper` parses them. `AVPairUtils` supplies target-info sequence handling.

## Risks and Test Signals
The parser assumes Unicode target names and trusts buffer pointers. It does not validate reserved bytes or signature/type itself beyond field assignment. Tests should round-trip server-created challenges, parse Windows challenge vectors, handle missing target info, and reject/trap truncated buffers in callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/ChallengeMessage.cs -->
