<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ReadWriteResponseHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ReadWriteResponseHelper.cs

## Purpose
SMB2 read, write, and flush command handling. It validates open file IDs, enforces read/write share access for file-system shares, delegates byte I/O to the backing store, and returns SMB2 count/data responses.

## APIs, Types, and Functions
The public helpers are `GetReadResponse()`, `GetWriteResponse()`, and `GetFlushResponse()`. They use `IFileStore.ReadFile()`, `WriteFile()`, `FlushFileBuffers()`, `ReadResponse`, `WriteResponse`, and `FlushResponse`.

## Control Flow, State, and Persistence
Read and write resolve `OpenFileObject` from the session. File-system shares invoke `HasReadAccess()` or `HasWriteAccess()` using the stored path before calling the file store. Successful reads copy returned bytes into `ReadResponse.Data`; writes return the number of bytes written. Flush only validates the file ID and calls the store. Persistent effects are in the backing store for writes and flushes.

## Dependencies and Integration
Called by SMB2 dispatch. It uses session open-file state and `FileSystemShare` access events.

## Risks and Test Signals
Risks include offset/read-length casts from unsigned protocol values to `long`/`int`, no enforcement of negotiated max read/write sizes here, and write authorization based on current path metadata that may change after rename. Test invalid IDs, denied access, EOF reads, partial writes, large offsets/lengths, flush errors, and named-pipe read/write paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/ReadWriteResponseHelper.cs -->
