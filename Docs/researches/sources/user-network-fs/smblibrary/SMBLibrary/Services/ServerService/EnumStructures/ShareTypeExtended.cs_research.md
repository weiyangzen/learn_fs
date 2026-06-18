<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/EnumStructures/ShareTypeExtended.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/EnumStructures/ShareTypeExtended.cs

## Purpose
Represents MS-SRVS share type values plus special and temporary high-bit flags for share information structures.

## APIs, Types, and Functions
Defines `ShareType : uint` values such as disk, print, device, IPC, and cluster variants. `ShareTypeExtended` stores `ShareType`, `IsSpecial`, and `IsTemporary`, with constructors from enum, flags, `NDRParser`, or raw `uint`, plus `Write()` and `ToUInt32()`.

## Control Flow, State, and Persistence
Raw values mask low 28 bits into `ShareType` and read high bits `0x80000000` and `0x40000000`. Writing recomposes the flags into a uint. No persistent state beyond struct fields.

## Dependencies and Integration
Used by `ShareInfo1Entry`, `ShareInfo2Entry`, and server service responses.

## Risks and Test Signals
Risks include silently accepting unknown low-bit share types and not preserving unrecognized high bits. Test round-trip serialization for disk, IPC, special, temporary, and cluster values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Services/ServerService/EnumStructures/ShareTypeExtended.cs -->
