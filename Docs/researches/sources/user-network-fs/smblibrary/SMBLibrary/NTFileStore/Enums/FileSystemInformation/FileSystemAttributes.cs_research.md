<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemAttributes.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemAttributes.cs

## Purpose
Defines the wire-level `FileSystemAttributes` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code. It is marked with `[Flags]`, so callers can combine values bitwise.

## Important APIs, Types, And Functions
The exported enum values include CaseSensitiveSearch = 0x0001, CasePreservedNames = 0x0002, UnicodeOnDisk = 0x0004, PersistentACLs = 0x0008, FileCompression = 0x0010, VolumeQuotas = 0x0020, SupportsSparseFiles = 0x0040, SupportsReparsePoints = 0x0080, SupportsRemoteStorage = 0x0100, ReturnsCleanupResultInfo = 0x0200, SupportsPOSIXUnlinkRename = 0x0400, VolumeIsCompressed = 0x8000, SupportsObjectIDs = 0x00010000, SupportsEncryption = 0x00020000, NamedStreams = 0x00040000, ReadOnlyVolume = 0x00080000, SequentialWriteOnce = 0x00100000, SupportsTransactions = 0x00200000, SupportsHardLinks = 0x00400000, SupportsExtendedAttributes = 0x00800000, SupportsOpenByFileID = 0x01000000, SupportsUSNJournal = 0x02000000, SupportsIntegrityStreams = 0x04000000, SupportsBlockRefCounting = 0x08000000, SupportsSparseVDL = 0x10000000. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

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
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/FileSystemAttributes.cs -->
