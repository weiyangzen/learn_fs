<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AVPairUtils.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AVPairUtils.cs

## Purpose
`AVPairUtils` reads and writes NTLM AV_PAIR target-info sequences used in challenge messages and NTLMv2 client challenges.

## Important APIs and Types
`GetAVPairSequence()` builds NetBIOS domain/computer name pairs. `GetAVPairSequenceBytes()`, `GetAVPairSequenceLength()`, and `WriteAVPairSequence()` serialize pairs plus the EOL terminator. `ReadAVPairSequence()` parses until `AVPairKey.EOL`.

## Control Flow
Serialization writes key and length as little-endian 16-bit values followed by the raw value. Deserialization peeks at the next key and repeatedly consumes pairs until EOL; EOL itself is not returned in the list.

## State, Dependencies, and Integration
The helper is stateless and depends on `KeyValuePairList`, endian readers/writers, and byte readers. `ChallengeMessage`, `NTLMv2ClientChallenge`, `IndependentNTLMAuthenticationProvider`, and SMB1 legacy NTLMv2 login all depend on its target-info encoding.

## Risks and Test Signals
Malformed sequences without EOL or with lengths beyond the buffer will throw from readers. There is no duplicate-key policy. Tests should include round trips for Unicode names, empty pair lists, unknown AV keys, missing EOL, and interoperability with Microsoft NTLM target-info vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Helpers/AVPairUtils.cs -->
