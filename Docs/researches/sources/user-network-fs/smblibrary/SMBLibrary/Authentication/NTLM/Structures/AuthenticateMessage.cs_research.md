<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/AuthenticateMessage.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/AuthenticateMessage.cs

## Purpose
`AuthenticateMessage` models the NTLM Type 3 AUTHENTICATE_MESSAGE and serializes/deserializes credentials, flags, optional version, and optional MIC.

## Important APIs and Types
Fields include LM/NT challenge responses, domain, user, workstation, encrypted random session key, negotiate flags, `NTLMVersion`, and `MIC`. `HasMicField()` detects MIC based on NTLMv2 AV flags. `GetBytes()` serializes the message. `CalculateMIC()` computes the HMAC-MD5 over negotiate, challenge, and authenticate bytes. `GetMicFieldOffset()` locates the MIC field.

## Control Flow
Parsing reads fixed security-buffer descriptors, decodes Unicode string fields, reads negotiate flags, optional version, and MIC if the NTLMv2 client challenge contains AV flags with bit `0x02`. Serialization lays out the fixed header, optional version/MIC, then payload strings/responses/session key, updating security-buffer pointers.

## State, Dependencies, and Integration
Client helpers build this object; server providers parse it. MIC and session key interactions depend on `NTLMCryptography`, `NTLMv2ClientChallenge`, and AV pairs.

## Risks and Test Signals
Serialization uses UTF-16 byte lengths via `string.Length * 2`; non-BMP characters need careful testing. MIC detection depends on AV pair parsing and `AVPairKey.Flags`. Tests should cover anonymous, v1, v2 with/without MIC, key-exchange field omission, and MIC offset when version is present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/AuthenticateMessage.cs -->
