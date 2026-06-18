<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryDirectory.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryDirectory.cs

## Purpose
`NTFileSystemAdapter.QueryDirectory.cs` implements directory enumeration and directory-entry information conversion for the managed adapter. It bridges SMB query-directory requests to `IFileSystem` directory listing and exact-entry lookup.

## Important APIs, Types, And Functions
The public entry point is `QueryDirectory(out List<QueryDirectoryFileInformation> result, object handle, string fileName, FileInformationClass informationClass)`. Helpers include `GetFiltered`, `ContainsWildcardCharacters`, `IsFileNameInExpression`, `FromFileSystemEntries`, and `FromFileSystemEntry`. Supported output classes include `FileBothDirectoryInformation`, `FileDirectoryInformation`, `FileFullDirectoryInformation`, `FileIdBothDirectoryInformation`, `FileIdFullDirectoryInformation`, and `FileNamesInformation`.

## Control Flow
The method rejects non-directory handles and empty names with `STATUS_INVALID_PARAMETER`. For wildcard expressions it lists entries in the handle path, filters by a simplified MS-FSA expression matcher, then injects cloned `.` and `..` entries. For exact names it resolves the parent directory path and calls `m_fileSystem.GetEntry(path + fileName)`. It converts entries to SMBLibrary directory information records and maps unsupported information levels to `STATUS_INVALID_INFO_CLASS`.

## State And Persistence
The operation is read-only. It reflects backing directory contents at call time and creates only transient cloned `FileSystemEntry` objects for `.` and `..`.

## Dependencies And Integration Points
The code depends on `DiskAccessLibrary.FileSystems.Abstractions` for entries and path helpers, the core adapter for exception mapping and allocation-size calculation, and SMBLibrary `QueryDirectoryFileInformation` subclasses. It is invoked by SMB1/SMB2 directory enumeration through the `INTFileStore.QueryDirectory` interface.

## Risks
Wildcard matching is only a subset of the MS-FSA rules: suffix `*`, leading DOS_STAR `<`, DOS_DOT `"`, and exact matches are handled, but arbitrary `?`, middle `*`, and complex DOS_QM behavior are not fully implemented. Exact lookup uses string concatenation after `GetDirectoryPath`, making path separator behavior dependent on `FileSystem` conventions. The wildcard path inserts `.` and `..` after filtering, so those entries are returned regardless of the expression. File IDs are emitted as zero.

## Test Signals
No direct directory adapter tests are present in this subset. Useful tests would cover wildcard expression edge cases, exact lookups, invalid handles, empty patterns, unsupported information classes, and `.`/`..` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryDirectory.cs -->
