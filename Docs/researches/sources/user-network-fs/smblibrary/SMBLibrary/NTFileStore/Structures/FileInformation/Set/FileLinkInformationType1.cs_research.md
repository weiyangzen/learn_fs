<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileLinkInformationType1.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileLinkInformationType1.cs

## Purpose
`FileLinkInformationType1` models an NT `set-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileLinkInformationType1 class. Fields include FixedLength:int, ReplaceIfExists:bool, RootDirectory:uint, FileNameLength:uint, FileName:string. Direct methods include FileLinkInformationType1, WriteBytes.

## Control Flow
The constructor reads the fixed little-endian fields from the supplied offset. `WriteBytes` serializes the fields back to the protocol layout, including UTF-16 names for rename/link records where present.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/FileLinkInformationType1.cs -->
