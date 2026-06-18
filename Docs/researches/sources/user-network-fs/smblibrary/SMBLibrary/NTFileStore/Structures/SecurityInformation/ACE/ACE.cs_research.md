<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/ACE.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/ACE.cs

## Purpose
`ACE` is the abstract base for access-control entries inside SMB security descriptors.

## Important APIs, Types, And Functions
Direct types: ACE class. Fields include Header:AceHeader. Direct methods include WriteBytes, GetAce.

## Control Flow
`GetAce` reads the ACE header type and dispatches to `AccessAllowedACE` or `AccessDeniedACE`; subclasses provide `WriteBytes` and `Length`.

## State And Persistence Behavior
State is the parsed in-memory representation of one IOCTL or security descriptor component. Persistence is only through SMB buffers or backend security metadata.

## Dependencies And Integration Points
Depends on `AceHeader`, ACE type enums, SID, access masks, ACL/security descriptor parsing.

## Risks
Risks include malformed buffer lengths, GUID/SID byte-order expectations, variable name length mismatches, unsupported ACE types, and offset advancement errors.

## Test Signals
Test parse/write round trips, fixed lengths, unsupported ACE dispatch, SID/mask preservation, and integration through IOCTL or security descriptor query/set operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/SecurityInformation/ACE/ACE.cs -->
