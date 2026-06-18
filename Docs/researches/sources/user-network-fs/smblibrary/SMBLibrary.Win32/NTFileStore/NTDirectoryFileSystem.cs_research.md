<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/NTDirectoryFileSystem.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/NTDirectoryFileSystem.cs

## Purpose
`NTDirectoryFileSystem.cs` implements `INTFileStore` directly over Windows native NT APIs rooted at a local directory. It exposes real NT create/read/write/query/set/notify/FSCTL behavior to SMBLibrary server code.

## Important APIs, Types, And Functions
The file defines `UNICODE_STRING`, `OBJECT_ATTRIBUTES`, `IO_STATUS_BLOCK`, `PendingRequest`, and `NTDirectoryFileSystem`. It P/Invokes `NtCreateFile`, `NtClose`, `NtReadFile`, `NtWriteFile`, `NtFlushBuffersFile`, `NtLockFile`, `NtUnlockFile`, `NtQueryDirectoryFile`, `NtQueryInformationFile`, `NtSetInformationFile`, `NtQueryVolumeInformationFile`, `NtSetVolumeInformationFile`, `NtQuerySecurityObject`, `NtSetSecurityObject`, `NtNotifyChangeDirectoryFile`, `NtFsControlFile`, `NtAlertThread`, and `NtCancelSynchronousIoFile`.

## Control Flow
Paths are converted to native `\??\root\relative` strings. `CreateFile` forces `SYNCHRONIZE` and synchronous alert I/O, adjusts incompatible append/no-buffering access, and calls `NtCreateFile`. Read, write, flush, lock, unlock, query-directory, query-info, set-info, volume-info, security stubs, notify, cancel, and FSCTL dispatch map the `INTFileStore` contract to native calls and parse returned byte buffers into SMBLibrary structures.

## State And Persistence
The store persists all file changes directly in the Windows filesystem under `m_directory`. It keeps an in-memory `PendingRequestCollection` for outstanding notify-change requests. Notify worker threads hold buffers and `PendingRequest` state until completion or cancellation.

## Dependencies And Integration Points
It depends on Windows `ntdll.dll`, kernel32 thread helpers, SMBLibrary file-information parsers, `ByteReader`, `ProcessHelper`, and `PendingRequestCollection`. It is the Win32 concrete file store used by SMB server integrations and tested by `NTDirectoryFileSystemTests`.

## Risks
Native interop is high risk: `UNICODE_STRING.MaximumLength` appears to use character count plus two rather than bytes, and `OBJECT_ATTRIBUTES.ObjectName` allocations are not freed after `NtCreateFile`. `QueryDirectory` and other methods compute `numberOfBytesWritten` but do not always use it. In `SetFileInformation`, the `FileLinkInformationType2` branches build local objects but assign `information = fileLinkInformationRemote`, likely losing the native path conversion. Notify cancellation has acknowledged race windows and uses worker threads plus alert/cancel APIs. Security get/set return invalid-device-request despite P/Invoke declarations existing.

## Test Signals
`NTDirectoryFileSystemTests` covers notify cancellation on Windows. Broader API behavior is largely untested in this subset and depends on Windows native API behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Win32/NTFileStore/NTDirectoryFileSystem.cs -->
