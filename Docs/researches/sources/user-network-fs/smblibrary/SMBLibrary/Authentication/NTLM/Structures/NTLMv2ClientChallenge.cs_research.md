<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMv2ClientChallenge.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMv2ClientChallenge.cs

## Purpose
`NTLMv2ClientChallenge` models the NTLMv2 client challenge blob appended to an NT proof string.

## Important APIs and Types
Fields include current/max version, timestamp, 8-byte client challenge, reserved fields, and AV pairs. Constructors build from domain/computer names, from target-info plus optional SPN, or parse bytes. `GetBytes()` serializes the structure and `GetBytesPadded()` appends the four zero bytes required for NTLMv2 proof calculation.

## Control Flow
Parsing reads fixed fields at offsets 0..27 and then delegates AV pair parsing at offset 28. Serialization writes fixed fields, FILETIME timestamp, client challenge, reserved fields, and the AV pair sequence.

## State, Dependencies, and Integration
Client authentication uses it to form NTLMv2 responses; server authentication parses it to validate proofs and detect MIC flags. Dependencies include `AVPairUtils`, `FileTimeHelper`, and endian/byte helpers.

## Risks and Test Signals
Constructors reuse the target-info list by reference and append SPN directly, mutating caller-owned collections. The timestamp epoch constant is not otherwise used. Tests should cover proof-vector serialization, padded bytes, SPN insertion side effects, malformed AV pairs, and MIC flag parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMv2ClientChallenge.cs -->
