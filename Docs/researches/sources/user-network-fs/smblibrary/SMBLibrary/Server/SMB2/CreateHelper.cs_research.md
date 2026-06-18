<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CreateHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CreateHelper.cs

## Purpose
SMB2 create/open command handling. It normalizes paths, checks share access for file-system shares, opens or creates the object in the backing store, allocates a SMB2 `FileID`, and returns create metadata.

## APIs, Types, and Functions
`CreateHelper.GetCreateResponse()` is the main entry. Private helpers build pipe and file-system `CreateResponse` instances. It uses `NTFileStoreHelper.ToCreateFileAccess()`, `IFileStore.CreateFile()`, `SMB2Session.AddOpenFile()`, and `NTFileStoreHelper.GetNetworkOpenInformation()`.

## Control Flow, State, and Persistence
The request name is forced to a leading backslash. Desired access is augmented with `FILE_READ_ATTRIBUTES` so metadata can be returned. On access denial or file-store error an SMB2 error is returned. On success, the backing handle and computed `FileAccess` are stored in the session open-file table; allocation failure closes the store handle. Named pipes get a minimal normal-file-attributes response.

## Dependencies and Integration
Called by `SMBServer.SMB2.cs` and feeds compounding support because create responses generate file IDs for related operations. It integrates with `FileSystemShare`, `NamedPipeShare`, security contexts, and `INTFileStore`.

## Risks and Test Signals
Risks include broadening desired access with read-attributes, path-normalization edge cases, no create-context handling, and assuming file info is non-null for file-system stores. Test create/open dispositions, denied reads/writes, named-pipe opens, too-many-open-files cleanup, compounded create/read/close, and returned metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/CreateHelper.cs -->
