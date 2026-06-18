<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsSizeInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsSizeInformation.cs

## Purpose
`FileFsSizeInformation` models a filesystem information record returned by SMB filesystem query operations.

## Important APIs, Types, And Functions
Direct types: FileFsSizeInformation class. Fields include FixedLength:int, TotalAllocationUnits:long, AvailableAllocationUnits:long, SectorsPerAllocationUnit:uint, BytesPerSector:uint. Direct methods include FileFsSizeInformation, WriteBytes.

## Control Flow
The constructor reads fixed fields and any variable UTF-16 string or byte-array data from the response buffer. `WriteBytes` serializes the same layout, and `Length` accounts for fixed and variable portions.

## State And Persistence Behavior
State is the parsed filesystem metadata. It is persisted only as SMB response bytes or applied backend filesystem settings where a store supports that.

## Dependencies And Integration Points
Depends on little-endian conversion helpers, FILETIME conversion for volume creation time where present, filesystem enums, and the `FileSystemInformation` factory.

## Risks
Risks include incorrect string byte counts, fixed-length mismatch, assuming a 48-byte object-id extended info buffer, and incomplete support for less common filesystem info classes.

## Test Signals
Test byte fixtures for each class, `Length` calculations, UTF-16 volume/filesystem names, sector-size flags, object-id buffers, and integration through `GetFileSystemInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileFsSizeInformation.cs -->
