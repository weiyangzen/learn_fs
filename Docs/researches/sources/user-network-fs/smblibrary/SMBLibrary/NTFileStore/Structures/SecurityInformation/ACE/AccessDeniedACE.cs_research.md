<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AccessDeniedACE.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AccessDeniedACE.cs

## Purpose
`AccessDeniedACE` models a concrete discretionary ACL entry with an access mask and SID.

## Important APIs, Types, And Functions
Direct types: AccessDeniedACE class. Fields include FixedLength:int, Mask:AccessMask, Sid:SID. Direct methods include AccessDeniedACE, WriteBytes.

## Control Flow
The constructor reads the ACE header, access mask, and SID. `WriteBytes` fills the header size, writes the header, mask, and SID, and advances the caller's offset.

## State And Persistence Behavior
State is the parsed in-memory representation of one IOCTL or security descriptor component. Persistence is only through SMB buffers or backend security metadata.

## Dependencies And Integration Points
Used by ACL and security descriptor serialization, with dependencies on `AceHeader`, `AccessMask`, and `SID`.

## Risks
Risks include malformed buffer lengths, GUID/SID byte-order expectations, variable name length mismatches, unsupported ACE types, and offset advancement errors.

## Test Signals
Test parse/write round trips, fixed lengths, unsupported ACE dispatch, SID/mask preservation, and integration through IOCTL or security descriptor query/set operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/AccessDeniedACE.cs -->
