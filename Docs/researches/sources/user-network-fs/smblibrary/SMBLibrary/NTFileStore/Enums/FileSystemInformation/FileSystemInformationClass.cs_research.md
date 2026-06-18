<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemInformationClass.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemInformationClass.cs

## Purpose
Defines the wire-level `FileSystemInformationClass` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include FileFsVolumeInformation = 0x01, FileFsLabelInformation = 0x02, FileFsSizeInformation = 0x03, FileFsDeviceInformation = 0x04, FileFsAttributeInformation = 0x05, FileFsControlInformation = 0x06, FileFsFullSizeInformation = 0x07, FileFsObjectIdInformation = 0x08, FileFsDriverPathInformation = 0x09, FileFsVolumeFlagsInformation = 0x0A, FileFsSectorSizeInformation = 0x0B. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemInformationClass.cs -->
