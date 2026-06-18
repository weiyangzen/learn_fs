<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileAttributes.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileAttributes.cs

## Purpose
Defines the wire-level `FileAttributes` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include ReadOnly = 0x00000001, Hidden = 0x00000002, System = 0x00000004, Directory = 0x00000010, Archive = 0x00000020, Normal = 0x00000080, Temporary = 0x00000100, SparseFile = 0x00000200, ReparsePoint = 0x00000400, Compressed = 0x00000800, Offline = 0x00001000, NotContentIndexed = 0x00002000, Encrypted = 0x00004000, IntegrityStream = 0x00008000, NoScrubData = 0x00020000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileAttributes.cs -->
