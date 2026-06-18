<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/FileInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/FileInformation.cs

## Purpose
`FileInformation` is the abstract base for NT file information records used by SMB query/set-info operations.

## Important APIs, Types, And Functions
Subclasses implement `WriteBytes`, `FileInformationClass`, and `Length`; `GetBytes` allocates a correctly sized buffer; static `GetFileInformation` dispatches a buffer and class code to supported concrete record types.

## Control Flow
Callers parse a response by passing the wire buffer and `FileInformationClass`; the switch constructs the matching class or throws `UnsupportedInformationLevelException`/`NotImplementedException`. Serialization is delegated to the concrete subclass.

## State And Persistence Behavior
The base class has no state. Concrete instances carry parsed metadata until serialized or consumed.

## Dependencies And Integration Points
Used by SMB1/SMB2 QueryInfo/SetInfo handlers and client file-store APIs. It depends on all concrete file-information classes and the `FileInformationClass` enum.

## Risks
Unsupported classes throw at runtime, and the factory defaults to Type2 rename/link layouts. New information classes must update both enum and factory or query paths will fail.

## Test Signals
Factory coverage should instantiate every supported class from bytes and verify `GetBytes` round trips; unsupported classes should return the expected exception/status mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/FileInformation.cs -->
