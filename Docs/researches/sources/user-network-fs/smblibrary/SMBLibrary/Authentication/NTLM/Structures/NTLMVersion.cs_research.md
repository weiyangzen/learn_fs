<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMVersion.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMVersion.cs

## Purpose
`NTLMVersion` represents the optional 8-byte NTLM VERSION structure.

## Important APIs and Types
Fields are product major/minor version, build, and current revision. `Length` is 8 and `NTLMSSP_REVISION_W2K3` is `0x0F`. Static factories expose `WindowsXP` and `Server2003`. `WriteBytes()` serializes the structure and `ToString()` returns major.minor.build.

## Control Flow
The byte constructor reads major/minor/build from the first four bytes and revision from byte 7, skipping the reserved three bytes. The writer mirrors that layout.

## State, Dependencies, and Integration
Message structures include this object when `NegotiateFlags.Version` is set. Client and server helpers currently advertise `Server2003`.

## Risks and Test Signals
Reserved bytes are left zero by default when writing but are not validated when reading. Tests should round-trip both static versions, parse known version bytes, verify optional inclusion in negotiate/challenge/authenticate messages, and assert `Length`-based offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Authentication/NTLM/Structures/NTLMVersion.cs -->
