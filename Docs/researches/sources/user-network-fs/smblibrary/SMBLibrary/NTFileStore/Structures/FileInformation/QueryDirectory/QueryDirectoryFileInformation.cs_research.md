<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/QueryDirectoryFileInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/QueryDirectoryFileInformation.cs

## Purpose
`QueryDirectoryFileInformation` models an NT `directory enumeration entry` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: QueryDirectoryFileInformation class. Fields include NextEntryOffset:uint, FileIndex:uint. Direct methods include QueryDirectoryFileInformation, WriteBytes, ReadFileInformation, ReadFileInformationList, GetBytes, GetListLength.

## Control Flow
Constructors read the common `NextEntryOffset`/`FileIndex` header plus the class-specific fixed fields and UTF-16 name fields. `WriteBytes` writes the same layout. List helpers on `QueryDirectoryFileInformation` align non-final entries to 8-byte boundaries and follow `NextEntryOffset` until zero.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/QueryDirectory/QueryDirectoryFileInformation.cs -->
