<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileSystemInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileSystemInformation.cs

## Purpose
`FileSystemInformation` is the abstract base and factory for NT filesystem information records used by SMB QueryInfo with `InfoType.FileSystem`.

## Important APIs, Types, And Functions
Subclasses implement `WriteBytes`, `FileSystemInformationClass`, and `Length`; `GetBytes` serializes an instance; static `GetFileSystemInformation` dispatches class codes to concrete filesystem information types.

## Control Flow
Factory control flow switches on `FileSystemInformationClass` and returns volume, size, device, attribute, control, full-size, object-id, or sector-size records. Unsupported classes throw `UnsupportedInformationLevelException`.

## State And Persistence Behavior
The base class has no retained state; subclasses carry one parsed filesystem metadata response.

## Dependencies And Integration Points
Used by SMB1/SMB2 file stores and server query-info handlers to expose volume and filesystem capabilities.

## Risks
Factory drift is the main risk: enum values without concrete parser support become runtime failures. Buffer size assumptions also matter because some strings are variable length.

## Test Signals
Test every supported filesystem info class with parse/write round trips and unsupported class error mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileSystemInformation/FileSystemInformation.cs -->
