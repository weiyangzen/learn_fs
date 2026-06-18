# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerProc.h

## Purpose

`MetadataManagerProc.h` declares the MetadataManager minifilter’s function interfaces and inline lock helpers.

It groups prototypes by implementation file:

- `operations.c`
- `DataStore.c`
- `support.c`

It also defines a helper macro for resource ownership and inline wrappers around `ERESOURCE` acquisition/release.

## Macro

### `MAKE_RESOURCE_OWNER`

```c
#define MAKE_RESOURCE_OWNER(X) (((ERESOURCE_THREAD)(X)) | 0x3)
```

This creates an `ERESOURCE_THREAD` owner value from an input pointer/thread-like value by setting low bits. It matches the resource ownership style used in Windows filesystem code.

## Operation Callback Prototypes

The header declares minifilter callbacks implemented in `operations.c`:

- `FmmPreCreate`
- `FmmPostCreate`
- `FmmPreCleanup`
- `FmmPostCleanup`
- `FmmPreFSControl`
- `FmmPostFSControl`
- `FmmPreDeviceControl`
- `FmmPostDeviceControl`
- `FmmPreShutdown`
- `FmmPrePnp`
- `FmmPostPnp`

The signatures match Filter Manager pre/post operation callback types and include SAL annotations for callback data, related objects, completion context, and post-operation flags.

## Data Store Prototypes

The header declares metadata lifecycle routines implemented in `DataStore.c`:

- `FmmOpenMetadata`
- `FmmCloseMetadata`
- `FmmReleaseMetadataFileReferences`
- `FmmReacquireMetadataFileReferences`
- `FmmSetMetadataOpenTriggerFileObject`
- `FmmBeginFileSystemOperation`
- `FmmEndFileSystemOperation`
- Optional `FmmIsMetadataOpen` when `VERIFY_METADATA_OPENED` is enabled.

The prototypes document important lock contracts with SAL:

- `FmmOpenMetadata` and `FmmCloseMetadata` require the global critical region and `InstanceContext->MetadataResource`.
- `FmmBeginFileSystemOperation` releases both the critical region and metadata resource.
- `FmmEndFileSystemOperation` reacquires them.
- `FmmIsMetadataOpen` has its own conditional compile contract.

These annotations are part of the sample’s concurrency documentation.

## Support Routine Prototypes

The header declares utility routines from `support.c`:

- `FmmAllocateUnicodeString`
- `FmmFreeUnicodeString`
- `FmmTargetIsVolumeOpen`
- `FmmIsImplicitVolumeLock`

These support buffer allocation, target-file-object classification, and implicit volume lock detection.

## Inline Lock Helpers

### `FmmAcquireResourceExclusive`

- Requires IRQL <= APC_LEVEL.
- Enters a critical region.
- Acquires an `ERESOURCE` exclusive.
- Asserts there is no incompatible shared/exclusive acquisition.

### `FmmAcquireResourceShared`

- Requires IRQL <= APC_LEVEL.
- Enters a critical region.
- Acquires an `ERESOURCE` shared.

### `FmmReleaseResource`

- Asserts the resource is held.
- Releases the `ERESOURCE`.
- Leaves the critical region.

These helpers centralize the rule that metadata-resource acquisition pairs with `KeEnterCriticalRegion`/`KeLeaveCriticalRegion`, blocking normal kernel APC delivery while the resource is held.

## Research Notes

This header is the contract file for the sample. The most important details are the SAL lock annotations around metadata operations and the resource wrappers. Any implementation change to `DataStore.c` or `operations.c` should preserve these lock contracts.
