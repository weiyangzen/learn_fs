<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/SetFileTime.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/SetFileTime.cs

## Purpose
`SetFileTime` represents SMB set-info timestamp semantics, including null time and the special must-not-change sentinel.

## Important APIs, Types, And Functions
It exposes `MustNotChange`, nullable `Time`, `ToFileTimeUtc`, and `FromFileTimeUtc`.

## Control Flow
Constructors create either a sentinel or concrete nullable time. Conversion to FILETIME returns `-1` for must-not-change, `0` for null, or the UTC FILETIME. Conversion from FILETIME reverses those meanings.

## State And Persistence Behavior
The struct is value state only and persists as timestamp integers in file-basic-information buffers.

## Dependencies And Integration Points
Used by `FileTimeHelper` and `FileBasicInformation` for SMB set-file-basic-info operations.

## Risks
Confusing `0`, `-1`, null, and real times can unexpectedly clear or preserve timestamps.

## Test Signals
Test all sentinel conversions and round trips through `FileTimeHelper.ReadSetFileTime`/`WriteSetFileTime`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Structures/FileInformation/Set/SetFileTime.cs -->
