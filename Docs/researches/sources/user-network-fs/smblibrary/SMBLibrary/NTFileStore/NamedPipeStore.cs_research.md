<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NamedPipeStore.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NamedPipeStore.cs

## Purpose
`NamedPipeStore` implements `INTFileStore` for IPC named pipes backed by in-process RPC `RemoteService` instances.

## Important APIs, Types, And Functions
Important methods include `CreateFile`, `CloseFile`, `ReadFile`, `WriteFile`, `DeviceIOControl`, `GetFileInformation`, and placeholder implementations for unsupported file-store operations.

## Control Flow
Create resolves a pipe path to a registered service and returns a stream-like handle. Read/write delegate to the pipe handle buffers. `DeviceIOControl` handles pipe wait and pipe transceive/control codes for RPC transport. Metadata queries synthesize file information suitable for named pipes; most filesystem, directory, security, notify, lock, and set operations return unsupported statuses.

## State And Persistence Behavior
State is the service list plus per-open pipe handles/service buffers. There is no disk persistence; data is transient RPC pipe traffic.

## Dependencies And Integration Points
Depends on `SMBLibrary.RPC`, `SMBLibrary.Services`, pipe IOCTL request structures, and the `INTFileStore` contract. It is exposed through IPC$-style server shares.

## Risks
Pipe semantics differ from disk files, so returning the wrong status for unsupported operations can break clients. Buffer ownership and max-output handling in transceive paths are protocol-sensitive.

## Test Signals
Exercise RPC bind/transceive flows, opening known and unknown pipes, close cleanup, read/write ordering, FSCTL_PIPE_WAIT, FSCTL_PIPE_TRANSCEIVE, and unsupported operation status codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/NamedPipeStore.cs -->
