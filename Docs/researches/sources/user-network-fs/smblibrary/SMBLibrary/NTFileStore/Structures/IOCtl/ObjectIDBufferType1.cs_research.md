<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/ObjectIDBufferType1.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/ObjectIDBufferType1.cs

## Purpose
`ObjectIDBufferType1` models the 64-byte FSCTL object ID buffer containing object, birth volume, birth object, and domain GUIDs.

## Important APIs, Types, And Functions
Direct types: ObjectIDBufferType1 class. Fields include Length:int, ObjectId:Guid, BirthVolumeId:Guid, BirthObjectId:Guid, DomainId:Guid. Direct methods include ObjectIDBufferType1, GetBytes.

## Control Flow
The constructor reads four consecutive 16-byte GUIDs. `GetBytes` writes the GUIDs back in the same order.

## State And Persistence Behavior
State is the parsed in-memory representation of one IOCTL or security descriptor component. Persistence is only through SMB buffers or backend security metadata.

## Dependencies And Integration Points
Used by object-id IOCTL handlers and depends on GUID byte conversion helpers.

## Risks
Risks include malformed buffer lengths, GUID/SID byte-order expectations, variable name length mismatches, unsupported ACE types, and offset advancement errors.

## Test Signals
Test parse/write round trips, fixed lengths, unsupported ACE dispatch, SID/mask preservation, and integration through IOCTL or security descriptor query/set operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/ObjectIDBufferType1.cs -->
