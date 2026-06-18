<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryFileSystem.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryFileSystem.cs

## Purpose
`NTFileSystemAdapter.QueryFileSystem.cs` reports volume and filesystem metadata for the managed `IFileSystem` adapter. It provides SMB clients with synthetic disk geometry, capacity, capabilities, and filesystem control data.

## Important APIs, Types, And Functions
`GetFileSystemInformation(out FileSystemInformation result, FileSystemInformationClass informationClass)` supports `FileFsVolumeInformation`, `FileFsSizeInformation`, `FileFsDeviceInformation`, `FileFsAttributeInformation`, `FileFsControlInformation`, `FileFsFullSizeInformation`, `FileFsObjectIdInformation`, and `FileFsSectorSizeInformation`. `SetFileSystemInformation(FileSystemInformation information)` always returns `STATUS_NOT_SUPPORTED`.

## Control Flow
The query method switches by information class. It uses adapter constants `BytesPerSector = 512` and `ClusterSize = 4096`, reports total and free allocation units from `m_fileSystem.Size` and `m_fileSystem.FreeSpace`, marks the device as a mounted disk, advertises case-preserved Unicode names, returns the backing filesystem name, and rejects object ID support with `STATUS_INVALID_PARAMETER`.

## State And Persistence
There is no persisted or mutable state. Values are either fixed constants or current properties from `m_fileSystem`.

## Dependencies And Integration Points
The file depends on the partial adapter's `m_fileSystem` and constants. It implements the `INTFileStore.GetFileSystemInformation` path used by SMB filesystem-info requests.

## Risks
Geometry is synthetic and may not match the backing implementation. Capabilities are conservative but incomplete: named streams are not advertised here even though other adapter code can list them. Quota values are set to `UInt64.MaxValue`; clients that interpret quotas strictly may get unrealistic values. Filesystem mutation through set-info is unsupported.

## Test Signals
No direct tests in this subset validate these returned structures. Coverage would need assertions for capacity rounding, advertised attributes, sector-size information, object-ID rejection, and unsupported set-info.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary.Adapters/NTFileSystemAdapter/NTFileSystemAdapter.QueryFileSystem.cs -->
