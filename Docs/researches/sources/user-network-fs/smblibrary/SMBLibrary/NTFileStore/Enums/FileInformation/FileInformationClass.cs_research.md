<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileInformationClass.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileInformationClass.cs

## Purpose
Defines the wire-level `FileInformationClass` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include FileDirectoryInformation = 0x01, FileFullDirectoryInformation = 0x02, FileBothDirectoryInformation = 0x03, FileBasicInformation = 0x04, FileStandardInformation = 0x05, FileInternalInformation = 0x06, FileEaInformation = 0x07, FileAccessInformation = 0x08, FileNameInformation = 0x09, FileRenameInformation = 0x0A, FileLinkInformation = 0x0B, FileNamesInformation = 0x0C, FileDispositionInformation = 0x0D, FilePositionInformation = 0x0E, FileFullEaInformation = 0x0F, FileModeInformation = 0x10, FileAlignmentInformation = 0x11, FileAllInformation = 0x12, FileAllocationInformation = 0x13, FileEndOfFileInformation = 0x14, FileAlternateNameInformation = 0x15, FileStreamInformation = 0x16, FilePipeInformation = 0x17, FilePipeLocalInformation = 0x18, FilePipeRemoteInformation = 0x19, FileCompressionInformation = 0x1C, FileNetworkOpenInformation = 0x22, FileAttributeTagInformation = 0x23, FileIdBothDirectoryInformation = 0x25, FileIdFullDirectoryInformation = 0x26, FileValidDataLengthInformation = 0x27, FileShortNameInformation = 0x28. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileInformation/FileInformationClass.cs -->
