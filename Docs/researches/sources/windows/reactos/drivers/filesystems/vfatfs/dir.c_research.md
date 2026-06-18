# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/dir.c

Purpose: Implements IRP_MJ_DIRECTORY_CONTROL for VFAT, including directory queries and directory change notifications. It converts DOS/FAT timestamps to NT system time, formats results for Windows directory information classes, and delegates actual entry scanning to the directory-entry layer.

Key routines:
- `FsdDosDateTimeToSystemTime` and `FsdSystemTimeToDosDateTime` translate FAT/FATX date/time fields using `DeviceExt->BaseDateYear` and local/system time conversion helpers.
- `VfatGetFileNamesInformation`, `VfatGetFileDirectoryInformation`, `VfatGetFileFullDirectoryInformation`, and `VfatGetFileBothInformation` populate caller buffers for `FileNamesInformation`, `FileDirectoryInformation`, `FileFullDirectoryInformation`, and `FileBothDirectoryInformation`.
- `DoQuery` handles query-directory state, search-pattern allocation, restart/index flags, shared/exclusive resource acquisition, repeated `FindFile` calls, output chaining through `NextEntryOffset`, and `IoStatus.Information`.
- `VfatNotifyChangeDirectory` registers notify IRPs through `FsRtlNotifyFullChangeDirectory`.
- `VfatDirectoryControl` dispatches `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`.

Implementation notes:
- FAT and FATX metadata are formatted separately. FATX has access time fields, while normal FAT uses access date with zero time.
- Directory entries report zero EOF/allocation size for directories in most query formats; file allocation is rounded to `BytesPerCluster`.
- Query state is kept in the CCB search pattern and entry index. A missing search pattern defaults to `*`.
- If resources cannot be acquired synchronously, the IRP user buffer is locked and the request is queued with `STATUS_PENDING`.
- The first output entry may return partial-name data with `STATUS_BUFFER_OVERFLOW`; subsequent entries require enough room for the complete variable-length entry.

Dependencies and interactions:
- Uses `FindFile`/`VfatGetNextDirEntry` from the directory-entry dispatch path, FCB `MainResource`, VCB `DirResource`, `VfatGetUserBuffer`, `VfatLockUserBuffer`, and FsRtl notification infrastructure.
- Directory-query output relies on `VFAT_DIRENTRY_CONTEXT` carrying both long and short Unicode names plus the raw FAT/FATX entry.

Notable limitations:
- FileIndex population is mostly left as comments except for the common `FILE_NAMES_INFORMATION`-compatible header path.
- The user-buffer probe is disabled behind `#if 0`, with a comment about SEH availability.
