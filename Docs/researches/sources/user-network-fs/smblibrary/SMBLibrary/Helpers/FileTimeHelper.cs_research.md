<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Helpers/FileTimeHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Helpers/FileTimeHelper.cs

## Purpose
`FileTimeHelper` centralizes conversion between Windows FILETIME wire integers and .NET `DateTime`/`SetFileTime` values for SMB file metadata.

## Important APIs, Types, And Functions
Important APIs include `ReadFileTimeSafe`, `ReadFileTime`, nullable read/write overloads, `WriteFileTime`, `ReadSetFileTime`, and `WriteSetFileTime`.

## Control Flow
Readers pull little-endian signed 64-bit FILETIME values from buffers and convert to UTC `DateTime`; safe reads clamp values above .NET's maximum. Nullable helpers map zero to null. `SetFileTime` helpers preserve the special no-change sentinel.

## State And Persistence Behavior
No retained state beyond constants for the Windows epoch minimum and .NET maximum FILETIME. Persistence is only the serialized timestamp fields in SMB structures.

## Dependencies And Integration Points
Used by file and filesystem information structures, especially basic/network-open/volume metadata and set-info timestamps.

## Risks
Timestamp edge cases are easy to mishandle: pre-1601 values, null/zero, max-value clamping, local-vs-UTC confusion, and the `SetFileTime` no-change sentinel need explicit coverage.

## Test Signals
Use boundary tests for zero, 1601-01-01 UTC, normal values, `DateTime.MaxValue`, over-max safe reads, nullable writes, and `SetFileTime.MustNotChange` round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Helpers/FileTimeHelper.cs -->
