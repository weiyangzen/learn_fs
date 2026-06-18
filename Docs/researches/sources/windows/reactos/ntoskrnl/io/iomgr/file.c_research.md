# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/file.c

This file implements ReactOS I/O manager file-object handling: file creation/open parsing, file object cleanup/delete/close, security descriptor access, name queries, stream file objects, share-access accounting, open cancellation, file-origin flags, and several Nt/Zw file syscalls.

Core open path:
- `IopCreateFile` is the main common implementation behind `IoCreateFile`, `IoCreateFileSpecifyDeviceObjectHint`, `NtCreateFile`, `NtOpenFile`, named pipe creation, and mailslot creation.
- It validates create parameters, probes user outputs, captures optional allocation size, copies and validates EA buffers, fills an `OPEN_PACKET`, calls `ObOpenObjectByName`, then reconciles Object Manager status with `OpenPacket.FinalStatus`.
- `IopParseDevice` is the main Object Manager parse routine for device/file opens. It builds an `IRP_MJ_CREATE`, `IRP_MJ_CREATE_NAMED_PIPE`, or `IRP_MJ_CREATE_MAILSLOT`, allocates a real `FILE_OBJECT` or a stack dummy object for query/delete-only paths, sends the IRP to the chosen device stack, waits when pending, and handles successful opens, failures, and reparses.
- `IopParseFile` handles relative opens through an existing file object by setting `OpenPacket->RelatedFileObject` and delegating to `IopParseDevice`.

Device/volume routing:
- `IopCheckDeviceAndDriver` rejects initializing, unloading, deleting, or removing device objects, enforces exclusive-device opens, and increments the device reference count on success.
- `IopParseDevice` handles related file objects, mounted VPBs, attached devices, direct device opens, volume opens, and optional top-level device hints.
- `IopCheckTopDeviceHint` validates hint use only for filesystem device stacks and rejects hints for direct opens or devices not found on the verified stack.
- Reparse traversal is bounded by `IOP_MAX_REPARSE_TRAVERSAL`; mount-point reparses can set `OpenPacket->TraversedMountPoint` and restart open processing.

Security and privilege handling:
- `IopCheckBackupRestorePrivilege` handles `FILE_OPEN_FOR_BACKUP_INTENT`, checking `SeBackupPrivilege` and `SeRestorePrivilege`, updating `ACCESS_STATE`, and clearing the backup-intent create option if neither privilege applies.
- `IopParseDevice` performs device security checks, traverse checks, secure-open checks, audit calls, and generic access mapping before creating the lower IRP.
- `IopGetSetSecurityObject` handles security query/set/assign/delete for both device objects and file objects. Device security can be read or changed directly; file security is sent down as `IRP_MJ_QUERY_SECURITY` or `IRP_MJ_SET_SECURITY`.
- `IopSetDeviceSecurityDescriptor` updates cached security descriptors under `IopSecurityResource`, retrying if another thread swaps the descriptor concurrently.
- `IopSetDeviceSecurityDescriptors` applies device security along the PDO-to-upper-device chain when a PDO is available.

File object lifetime:
- `IopDeleteFile` sends `IRP_MJ_CLOSE`, optionally sends cleanup first if no handle was created, adjusts VPB/device references, frees `FileName`, releases completion-port context, tears down per-file-object filter contexts, and dereferences the device object.
- `IopCloseFile` runs on handle close. It unlocks outstanding byte-range locks for the process, then sends `IRP_MJ_CLEANUP` on the last system handle.
- `IoCancelFileOpen` sends cleanup for an open that is being cancelled before `FO_HANDLE_CREATED`; calling it after a handle exists bugchecks with `INVALID_CANCEL_OF_FILE_OPEN`.

Name and attribute query helpers:
- `IopQueryNameInternal` combines the device/object name and filesystem `FileNameInformation`, optionally converting the volume device to a DOS name. Network filesystems get a simple root separator for DOS-name queries instead of mount-manager lookup.
- `IoQueryFileDosDeviceName` loops with increasing buffers until `IopQueryNameInternal` succeeds or fails for a reason other than `STATUS_BUFFER_OVERFLOW`.
- `IopQueryAttributesFile`, `NtQueryAttributesFile`, `NtQueryFullAttributesFile`, and `IoFastQueryNetworkAttributes` use dummy file objects and create parsing to obtain basic or network-open information without returning a real handle.

Stream file objects and extensions:
- `IoCreateStreamFileObjectEx`, `IoCreateStreamFileObject`, and `IoCreateStreamFileObjectLite` create internal stream file objects tied to a device or existing file object, mark them `FO_STREAM_FILE`, initialize events, and manage VPB/device references.
- `IopCreateFile` can allocate a `FILE_OBJECT_EXTENSION` for top-device hints.
- `IoGetFileObjectFilterContext` and `IoChangeFileObjectFilterContext` expose atomic get/define/clear behavior for extension filter contexts.

Share access and origin APIs:
- `IoCheckShareAccess`, `IoSetShareAccess`, `IoUpdateShareAccess`, and `IoRemoveShareAccess` implement standard read/write/delete share accounting against `SHARE_ACCESS`.
- `IoSetFileOrigin` toggles `FO_REMOTE_ORIGIN`; `IoIsFileOriginRemote` reads it.

Nt entry points:
- `NtCreateFile` and `NtOpenFile` delegate to `IoCreateFile`.
- `NtCreateMailslotFile` and `NtCreateNamedPipeFile` capture timeout parameters and pass create-specific parameter blocks through `IoCreateFile`.
- `NtCancelIoFile` cancels all IRPs in the current thread whose original file object matches the supplied handle, then waits until they leave the thread IRP list.
- `NtDeleteFile` opens with a dummy object, `FILE_DELETE_ON_CLOSE`, and delete-only semantics.
- `NtFlushWriteBuffer` wraps `KeFlushWriteBuffer`.

Research notes:
- `IoCheckQuerySetFileInformation` and `IoCheckQuotaBufferValidity` are explicit unimplemented stubs.
- `IoCreateFileSpecifyDeviceObjectHint` is marked `@unimplemented` in the comment but contains a working wrapper around `IopCreateFile` with file-object-extension and top-device-hint flags.
- The open path carefully distinguishes Object Manager parse status from the lower I/O status in `OpenPacket.FinalStatus`; callers generally use the lower status only after `ParseCheck` is set.
- Reparse handling is central and delicate: `IopDoNameTransmogrify` validates mount-point reparse data, rewrites `FileObject->FileName`, preserves a reserved suffix, and frees driver-supplied auxiliary reparse data.
- The share-access routines currently bypass checks/updates for any file object with `FO_FILE_OBJECT_HAS_EXTENSION` because the intended `IO_IGNORE_SHARE_ACCESS_CHECK` test is commented out.
- In the device `SetSecurityDescriptor` branch of `IopGetSetSecurityObject`, the function computes `Status` from the descriptor update path but returns `STATUS_SUCCESS`, which may hide device security update failures.
- Manual reference-count and cleanup ordering is a major correctness concern throughout this file: device references, VPB references, file-object references, IRP queueing, dummy file objects, and reparse retry paths all interact.
