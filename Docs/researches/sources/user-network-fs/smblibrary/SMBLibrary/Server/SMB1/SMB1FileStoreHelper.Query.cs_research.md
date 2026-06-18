# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/SMB1FileStoreHelper.Query.cs

## Purpose

Partial SMB1 file-store helper for querying file information by path or handle and converting NT file information to SMB1 query information levels.

## Important APIs, Types, And Functions

`GetFileInformation` overloads open a path for read attributes or query an existing handle. It maps SMB1 `QueryInformationLevel` to `FileInformationClass`, calls the file store, and converts through `QueryInformationHelper`.

## Control Flow

Path-based methods open the object with `FILE_READ_ATTRIBUTES`, query, close, and return status. Unsupported information levels return `STATUS_OS2_INVALID_LEVEL`.

## State And Persistence Behavior

No persistent mutations; opens are temporary and closed before return.

## Dependencies And Integration Points

Depends on `INTFileStore`, `QueryInformationHelper`, `UnsupportedInformationLevelException`, and `SecurityContext`.

## Risks And Edge Cases

Temporary opens can fail because of sharing conflicts even for metadata queries. Path-based file information class overload always uses `FILE_READ_ATTRIBUTES`, which may not be sufficient for every class.

## Test Signals

Test supported/unsupported levels, path and handle queries, close-on-error, sharing conflicts, and conversion correctness for timestamps, sizes, and attributes.

Source-read signal: reviewed the complete local source file for this item.
