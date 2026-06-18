<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2FileStore.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2FileStore.cs

## Purpose
`SMB2FileStore` adapts an authenticated SMB2 tree connection to the `ISMBFileStore` API for open, close, read, write, query, set, security, FSCTL, and tree disconnect operations.

## Important APIs, Types, And Functions
Important methods are `CreateFile`, `CloseFile`, `ReadFile`, `WriteFile`, `FlushFileBuffers`, `QueryDirectory`, `GetFileInformation`, `SetFileInformation`, `GetFileSystemInformation`, `GetSecurityInformation`, `SetSecurityInformation`, `DeviceIOControl`, `Disconnect`, and `MaxReadSize`/`MaxWriteSize`. Lock, unlock, notify, cancel, and filesystem-set operations currently throw `NotImplementedException`.

## Control Flow
Each operation builds the matching SMB2 request, assigns the tree ID, calculates credit charge for large read/write/query/ioctl buffers, sends through `SMB2Client.TrySendCommand`, waits by message ID, extracts typed response payloads on success, and maps missing responses to timeout or invalid-SMB status. Directory queries loop until the server stops returning `STATUS_SUCCESS` pages.

## State And Persistence Behavior
Persistent state is limited to the client reference, tree ID, and share encryption flag. File handles are SMB2 `FileID` objects returned by create/open and supplied by callers on later operations.

## Dependencies And Integration Points
Depends on SMB2 request/response classes, NT file-store structures (`FileInformation`, `FileSystemInformation`, `SecurityDescriptor`), and `SMB2Client` transport/session state. It is the client-side implementation behind `TreeConnect`.

## Risks
Several `INTFileStore` capabilities are absent. Query output buffers are fixed at 4096 for many information classes and may truncate larger descriptors. `GetFileSystemInformation` opens the share root and always closes it afterward, so failure between open and close would leak a remote handle. Credit charge calculation assumes 64 KiB credit units and that client max sizes are negotiated correctly.

## Test Signals
Test through SMB2 file lifecycle flows: create/open dispositions, large multi-credit reads and writes, paged directory enumeration, QueryInfo and SetInfo round trips, security descriptor query/set, IOCTL success and buffer overflow responses, encrypted share operation, and timeout/disconnect behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Client/SMB2FileStore.cs -->
