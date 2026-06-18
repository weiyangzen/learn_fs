<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CloseHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CloseHelper.cs

## Purpose
SMB2 close handling for open file objects. It validates the `FileId`, closes the backing store handle, removes the open-file table entry, and optionally returns post-close attributes.

## APIs, Types, and Functions
`CloseHelper.GetCloseResponse()` is the entry point. It uses `SMB2Session.GetOpenFileObject()`, `IFileStore.CloseFile()`, `NTFileStoreHelper.GetNetworkOpenInformation()`, and `CloseResponse`.

## Control Flow, State, and Persistence
The helper rejects unknown file IDs with `STATUS_FILE_CLOSED`. On successful store close, it removes the file from the session and, if `PostQueryAttributes` is set, queries path-based network-open information and copies timestamps, allocation size, EOF, and attributes to the response. State is per-session open-handle metadata; no persistent state is written here.

## Dependencies and Integration
Called from SMB2 dispatch after session/tree lookup. It integrates with any `ISMBShare` whose `FileStore` implements close and network-open information helpers.

## Risks and Test Signals
Risks include querying post-close attributes by path after the handle is closed, failure to remove the open-file object when `CloseFile()` returns an error, and stale metadata if the file was renamed or deleted. Test invalid file IDs, store close failures, post-query on existing and deleted files, and session table cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CloseHelper.cs -->
