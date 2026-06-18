<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NegotiateMessage.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NegotiateMessage.cs

## Purpose
`NegotiateMessage` models NTLM Type 1 NEGOTIATE_MESSAGE.

## Important APIs and Types
Fields are signature, message type, negotiate flags, optional domain name, optional workstation, and optional version. `GetBytes()` serializes the message; the byte constructor parses it.

## Control Flow
Parsing reads signature/type/flags, then ANSI buffer pointers for domain and workstation, and optional version at offset 32. Serialization clears domain/workstation unless their supplied flags are set, computes fixed length 32 or 40, writes fixed fields, then writes domain and workstation payloads.

## State, Dependencies, and Integration
Client helpers generate negotiate messages; server providers parse them. It depends on NTLM buffer-pointer helpers and `NTLMVersion`.

## Risks and Test Signals
Serialization writes UTF-16 payloads while parsing uses ANSI readers for domain/workstation, which is unusual for OEM-supplied fields and should be tested for interoperability. Tests should cover supplied/unsupplied names, version flag offsets, and parsing of Windows Type 1 vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NegotiateMessage.cs -->
