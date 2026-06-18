<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileCompressionInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileCompressionInformation.cs

## Purpose
`FileCompressionInformation` models an NT `query-info payload` used by SMB file metadata operations.

## Important APIs, Types, And Functions
Direct types: FileCompressionInformation class. Fields include FixedLength:int, CompressedFileSize:long, CompressionFormat:CompressionFormat, CompressionUnitShift:byte, ChunkShift:byte, ClusterShift:byte, Reserved:byte[]. Direct methods include FileCompressionInformation, WriteBytes.

## Control Flow
The constructor decodes the wire layout from a byte buffer. `WriteBytes` emits the same fields for server responses or set-info reuse where supported. Variable-length forms compute length from UTF-16 or ASCII payload fields.

## State And Persistence Behavior
State is the parsed metadata fields stored on the object. Persistence occurs only when an SMB server applies a set-info operation to a backend or when the object is serialized into a protocol response.

## Dependencies And Integration Points
Depends on little-endian readers/writers, `FileTimeHelper` for timestamp fields, UTF-16/ASCII string helpers for variable names or EAs, and `FileInformationClass` dispatch from query/set handlers.

## Risks
Risks include missing buffer length validation, incorrect fixed-length constants, UTF-16 byte-length vs character-count mistakes, 8-byte alignment errors in lists, and unsupported information class assumptions.

## Test Signals
Test byte-level parse/write round trips, declared `Length`, `FileInformationClass`, boundary names or EA values, directory list alignment, and integration through SMB2 QueryInfo/SetInfo or QueryDirectory.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Query/FileCompressionInformation.cs -->
