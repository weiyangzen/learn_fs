<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/PipeWaitRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/PipeWaitRequest.cs

## Purpose
`PipeWaitRequest` models the named-pipe wait FSCTL input buffer with timeout, time-specified flag, padding, and pipe name.

## Important APIs, Types, And Functions
Direct types: PipeWaitRequest class. Fields include FixedLength:int, Timeout:ulong, NameLength:uint, TimeSpecified:bool, Padding:byte, Name:string. Direct methods include PipeWaitRequest, GetBytes.

## Control Flow
The constructor reads timeout, name length, time flag, padding, and UTF-16 pipe name. `GetBytes` serializes the fixed header followed by the name.

## State And Persistence Behavior
State is the parsed in-memory representation of one IOCTL or security descriptor component. Persistence is only through SMB buffers or backend security metadata.

## Dependencies And Integration Points
Used by named-pipe IOCTL handling in `NamedPipeStore` and SMB server/client FSCTL paths.

## Risks
Risks include malformed buffer lengths, GUID/SID byte-order expectations, variable name length mismatches, unsupported ACE types, and offset advancement errors.

## Test Signals
Test parse/write round trips, fixed lengths, unsupported ACE dispatch, SID/mask preservation, and integration through IOCTL or security descriptor query/set operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/IOCtl/PipeWaitRequest.cs -->
