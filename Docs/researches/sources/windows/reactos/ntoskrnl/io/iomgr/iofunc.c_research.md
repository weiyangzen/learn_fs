# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iofunc.c

## Purpose

Implements the ReactOS kernel I/O manager’s generic file, volume, directory, device-control, paging, lock, read, and write entry points. This file is the main syscall-facing IRP construction layer for `Nt*File`, `Io*Information`, paging I/O, and device/filesystem control operations.

## Main Responsibilities

- Converts native APIs such as `NtReadFile`, `NtWriteFile`, `NtQueryInformationFile`, `NtSetInformationFile`, `NtDeviceIoControlFile`, `NtFsControlFile`, and volume information calls into initialized IRPs.
- Handles synchronous file object locking, file object events, caller events, APC/completion-port conflicts, pending waits, and interruption abort paths.
- Chooses buffered I/O, direct I/O with MDLs, or neither I/O based on device flags and IOCTL transfer method.
- Uses Fast I/O opportunistically for device controls, byte-range locks, basic/standard file information, reads, writes, and unlocks.
- Provides special kernel-handled answers for selected metadata such as file position, access/mode/alignment information, `FileFsDeviceInformation`, and `FileFsDriverPathInformation`.
- Implements paging read/write helpers `IoPageRead` and `IoSynchronousPageWrite`, including reserve IRP fallback for paging-file reads.

## Important Internal Helpers

- `IopCleanupAfterException` releases partially built IRPs, system buffers, MDLs, synchronous file locks, events, local events, and file object references after SEH failures.
- `IopFinalizeAsynchronousIo` waits on locally allocated events for async handles, aborts interrupted IRPs, copies the kernel IOSB back to the caller, and frees the event.
- `IopPerformSynchronousRequest` centralizes IRP queuing, operation-count accounting, `IoCallDriver`, deferred completion, synchronous waits, abort-on-alert/APC, and file-object unlock.
- `IopDeviceFsIoControl` is the common implementation behind `NtDeviceIoControlFile` and `NtFsControlFile`.
- `IopQueryDeviceInformation`, `IopGetFileInformation`, and `IopGetBasicInformationFile` provide kernel-mode query helpers.
- `IopOpenLinkOrRenameTarget` opens and validates rename/link target parent directories, checks overwrite rules, and enforces same-device targets.
- `IopGetFileMode`, `IopGetMountFlag`, `IopVerifyDriverObjectOnStack`, and `IopGetDriverPathInformation` synthesize selected query results without dispatching to the FSD.

## Public and Native APIs Covered

Implemented or substantially implemented:

- Paging and kernel helpers: `IoSynchronousPageWrite`, `IoPageRead`, `IoQueryFileInformation`, `IoQueryVolumeInformation`, `IoSetInformation`.
- Control: `NtDeviceIoControlFile`, `NtFsControlFile`.
- Flush and notification: `NtFlushBuffersFile`, `NtNotifyChangeDirectoryFile`.
- Locking: `NtLockFile`, `NtUnlockFile`.
- Directory query: `NtQueryDirectoryFile`.
- File information: `NtQueryInformationFile`, `NtSetInformationFile`.
- Read/write: `NtReadFile`, `NtWriteFile`.
- Volume information: `NtQueryVolumeInformationFile`, `NtSetVolumeInformationFile`.

Explicitly unimplemented stubs:

- `NtQueryEaFile`
- `NtQueryQuotaInformationFile`
- `NtReadFileScatter`
- `NtSetEaFile`
- `NtSetQuotaInformationFile`
- `NtWriteFileGather`
- `NtCancelDeviceWakeupRequest`
- `NtRequestDeviceWakeup`

## Behavior Notes

- User-mode callers are guarded with SEH probing for IOSBs, buffers, strings, offsets, keys, and information structures.
- Noncached read/write paths validate sector-size alignment, buffer alignment, and byte-offset alignment.
- Async file handles require explicit offsets for normal files; named pipes and mailslots are exceptions.
- `FO_SYNCHRONOUS_IO` paths use file-object locking and may use `FileObject->CurrentByteOffset` when caller passes `FILE_USE_FILE_POINTER_POSITION` or no byte offset.
- Completion ports and user APC routines are rejected together on the same request.
- Buffered I/O allocates `AssociatedIrp.SystemBuffer` and sets `IRP_BUFFERED_IO`, `IRP_DEALLOCATE_BUFFER`, and input/output flags as needed.
- Direct I/O allocates MDLs and probes/locks pages with `IoReadAccess` or `IoWriteAccess`.
- `IRP_DEFER_IO_COMPLETION` is used for several file/directory/query paths so this layer can complete immediately returned IRPs itself.
- `FSCTL_DISMOUNT_VOLUME` increments `SharedUserData->DismountCount`.

## Filesystem Relevance

This is the syscall-to-filesystem-driver boundary for ReactOS. Most filesystem-visible IRPs for read/write, metadata query/set, directory enumeration, notifications, byte-range locks, flushes, filesystem controls, and volume controls originate here. It is central for understanding how ReactOS presents Windows-compatible I/O manager behavior to local filesystems and filesystem filters.

## Dependencies and Coupling

Heavy dependencies include object manager handle referencing, file object flags, device stack lookup, Fast I/O dispatch tables, MDL allocation, memory probing/locking, completion ports, shared user data, cache manager counters, VPB mount state, and I/O completion internals.

## Research Notes

- The file is mostly implemented but still has notable syscall gaps around EAs, quota APIs, scatter/gather file I/O, and device wake requests.
- Error cleanup is spread through common helpers plus local SEH blocks; this file is a key place to audit for leak, double-unlock, and stale-event bugs.
- Fast I/O acceptance is conservative for read/write: only direct success-like statuses are accepted before falling back to IRPs.
