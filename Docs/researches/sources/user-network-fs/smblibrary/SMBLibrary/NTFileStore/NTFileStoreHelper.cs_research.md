<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NTFileStoreHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NTFileStoreHelper.cs

## Purpose
`NTFileStoreHelper` maps SMB/NT access masks and share modes to .NET file APIs and provides convenience queries for network-open information.

## Important APIs, Types, And Functions
Important APIs are `ToCreateFileAccess`, `ToFileAccess`, `ToFileShare`, and `GetNetworkOpenInformation` overloads for path or handle.

## Control Flow
Access conversion checks desired read/write/append bits and create disposition to choose .NET `FileAccess`. Share conversion maps SMB read/write/delete sharing to `FileShare`. Network-open helpers open or query a file through an `INTFileStore`, collect `FileNetworkOpenInformation`, and close temporary handles.

## State And Persistence Behavior
No global state. Temporary handles created for path-based queries must be closed before returning.

## Dependencies And Integration Points
Used by file-store implementations and server handlers that need to bridge SMB semantics with local .NET stream/file behavior.

## Risks
SMB generic access bits, append-only writes, overwrite dispositions, and delete sharing do not map perfectly to .NET flags. Helper-created handles can leak if future code adds throwing paths between open and close.

## Test Signals
Test access/share conversion matrices and `GetNetworkOpenInformation` success/failure/cleanup paths against real and fake stores.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NTFileStoreHelper.cs -->
