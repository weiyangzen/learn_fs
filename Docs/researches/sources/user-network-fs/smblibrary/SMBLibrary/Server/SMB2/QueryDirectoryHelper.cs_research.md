<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryDirectoryHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryDirectoryHelper.cs

## Purpose
SMB2 directory enumeration. It validates the open directory handle, enforces read access for file-system shares, starts or resumes an `OpenSearch`, pages results into the requested output buffer, and returns directory information records.

## APIs, Types, and Functions
`QueryDirectoryHelper.GetQueryDirectoryResponse()` is the entry point. It uses `SMB2Session.GetOpenFileObject()`, `GetOpenSearch()`, `AddOpenSearch()`, `IFileStore.QueryDirectory()`, and `QueryDirectoryResponse.SetFileInformationList()`.

## Control Flow, State, and Persistence
Unknown file IDs fail as closed. A new or reopened search calls the backing store and caches all matching entries in session state. `Restart` and `Reopen` reset enumeration. Empty result sets return `STATUS_NO_SUCH_FILE`; exhausted searches return `STATUS_NO_MORE_FILES`. Pagination accounts for eight-byte padded entry lengths and supports `ReturnSingleEntry`.

## Dependencies and Integration
Called by SMB2 dispatch after tree lookup. It assumes directory requests target `FileSystemShare` because it casts the share before access checks.

## Risks and Test Signals
Risks include the hard cast to `FileSystemShare`, storing full directory result lists in memory, returning an empty success if the first entry cannot fit, and rejecting file-information-class changes mid-search. Test reopen/restart/single-entry flags, tiny buffers, no matches, exhausted searches, access denial, large directories, and invalid file IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/QueryDirectoryHelper.cs -->
