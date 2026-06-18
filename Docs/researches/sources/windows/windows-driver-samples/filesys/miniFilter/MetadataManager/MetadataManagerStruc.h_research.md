# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerStruc.h

## Purpose

`MetadataManagerStruc.h` defines the MetadataManager sample’s core data structures, constants, flags, metadata filename, and debug tracing macros.

## Verification Flag

```c
#define VERIFY_METADATA_OPENED 0
```

When enabled, the filter validates that metadata is open whenever non-volume creates succeed. In the checked-in configuration it is disabled, so the create path can skip non-DASD I/O for performance.

## Pool Tags

Defined pool tags:

- `FMM_STRING_TAG`
- `FMM_INSTANCE_CONTEXT_TAG`

These tag Unicode string buffers and instance contexts.

## Global Data

`FMM_GLOBAL_DATA` contains:

- `PFLT_FILTER Filter`: handle returned by `FltRegisterFilter`.
- `ULONG DebugLevel`: checked-build-only debug trace mask.

The file declares:

```c
extern FMM_GLOBAL_DATA Globals;
```

The storage is defined in `MetadataManagerInit.c`.

## Instance Context Flags

### `INSTANCE_CONTEXT_F_TRANSITION`

Indicates the instance metadata resource was intentionally released before issuing a filesystem operation that could reenter the filter stack.

While this flag is set, other threads that acquire the resource should avoid using or modifying the instance context.

### `INSTANCE_CONTEXT_F_METADATA_OPENED`

Indicates the filter currently has an open handle and referenced file object for the volume’s metadata file.

## `FMM_INSTANCE_CONTEXT`

The per-volume instance context contains:

- `Flags`: instance flags.
- `Instance`: Filter Manager instance handle.
- `FilesystemType`: attached filesystem type.
- `Volume`: Filter Manager volume handle.
- `MetadataResource`: `ERESOURCE` protecting metadata state.
- `MetadataHandle`: metadata file handle.
- `MetadataFileObject`: referenced metadata file object.
- `MetadataOpenTriggerFileObject`: volume file object whose cleanup/unlock/cancel path should trigger metadata reopen.

This context is allocated in `FmmInstanceSetup`, associated with the instance, used by `DataStore.c`, and closed in teardown.

## Metadata File Name

The sample metadata path is:

```c
\System Volume Information\FilterMetadata.md
```

Constants:

- `FMM_METADATA_FILE_NAME`
- `FMM_METADATA_FILE_NAME_LENGTH`
- `FMM_DEFAULT_VOLUME_NAME_LENGTH`

The metadata open path appends this relative path to the volume name returned by `FltGetVolumeName`.

## Debug Trace Flags

Checked builds define trace categories:

- `DEBUG_TRACE_ERROR`
- `DEBUG_TRACE_LOAD_UNLOAD`
- `DEBUG_TRACE_INSTANCES`
- `DEBUG_TRACE_METADATA_OPERATIONS`
- `DEBUG_TRACE_ALL_IO`
- `DEBUG_TRACE_INFO`
- `DEBUG_TRACE_ALL`

`DebugTrace` expands to `DbgPrint` when the requested level is enabled in `Globals.DebugLevel`; otherwise it compiles to nothing.

## Research Notes

This header is the sample’s state model. The key design is that a minifilter can keep per-volume metadata state in an instance context, but must be prepared to drop actual file references when the filesystem needs exclusive volume access.
