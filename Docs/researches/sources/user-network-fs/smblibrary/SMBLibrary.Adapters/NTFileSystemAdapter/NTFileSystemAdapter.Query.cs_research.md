<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Query.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Query.cs

## Purpose
`NTFileSystemAdapter.Query.cs` implements `GetFileInformation` for the managed `IFileSystem`-backed `INTFileStore` adapter. It translates a subset of SMB/NT file information classes into SMBLibrary `FileInformation` records from `DiskAccessLibrary.FileSystems.Abstractions.FileSystemEntry` metadata.

## Important APIs, Types, And Functions
The main API is `GetFileInformation(out FileInformation result, object handle, FileInformationClass informationClass)`. It consumes the adapter's `FileHandle`, calls `m_fileSystem.GetEntry(path)`, and emits `FileBasicInformation`, `FileStandardInformation`, `FileInternalInformation`, `FileEaInformation`, `FileNameInformation`, `FileAllInformation`, `FileStreamInformation`, and `FileNetworkOpenInformation`. The helper `GetFileAttributes(FileSystemEntry entry)` maps hidden, read-only, archive, and directory flags to `FileAttributes`, defaulting to `Normal`.

## Control Flow
The method first resolves the current entry for the handle path and maps I/O or access exceptions through `ToNTStatus`. It then switches on `informationClass`, populating the requested structure with timestamps, allocation size via `GetAllocationSize`, EOF size, directory status, delete-pending state from the handle, name, and named-stream entries when requested. Unsupported but recognized classes return `STATUS_NOT_IMPLEMENTED`; unknown classes return `STATUS_INVALID_INFO_CLASS`.

## State And Persistence
This file is read-only with respect to the backing filesystem. It reflects current metadata from `m_fileSystem`; the only handle-local state it exposes is `DeleteOnClose`. It does not persist or cache information.

## Dependencies And Integration Points
It depends on the partial `NTFileSystemAdapter` core for `m_fileSystem`, `FileHandle`, `GetAllocationSize`, logging, and exception-to-status mapping. It integrates with SMB query-info handling through the `INTFileStore.GetFileInformation` contract and with named-stream support through `IFileSystem.ListDataStreams`.

## Risks
Many information classes are intentionally unimplemented, so clients needing access, position, EA, mode, alignment, compression, pipe, or attribute-tag data receive limited behavior. `FileInternalInformation` emits an empty structure without a stable file ID. `FileNameInformation` returns `entry.Name`, not necessarily a full path. Named stream enumeration assumes the backing `IFileSystem` implementation correctly models alternate data streams.

## Test Signals
This subset has no direct unit test for the adapter query mapping. Indirect coverage would come from SMB query-info flows or file-store integration tests that exercise `INTFileStore.GetFileInformation`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.Query.cs -->
