# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatstruc.h

## Purpose

`fatstruc.h` defines FastFAT’s core in-memory data structures. These are the objects manipulated by the routines declared in `fatprocs.h`: global driver data, mounted volumes, file/directory control blocks, per-handle context, IRP context, noncached I/O context, and EA helper ranges.

## Core Object Model

### `FAT_DATA`

Global FastFAT driver state, allocated from nonpaged pool.

Important fields:

- Node identity: `NodeTypeCode`, `NodeByteSize`.
- Mounted volume list: `VcbQueue`.
- Driver and filesystem device objects: `DriverObject`, `DiskFileSystemDeviceObject`, `CdromFileSystemDeviceObject`.
- Global synchronization: `Resource`, `GeneralSpinLock`.
- Cache integration: `OurProcess`, `CacheManagerCallbacks`, `CacheManagerNoOpCallbacks`.
- Runtime flags:
  - `ChicagoMode`
  - `FujitsuFMR`
  - `AsyncCloseActive`
  - `ShutdownStarted`
  - `CodePageInvariant`
  - `HighAsync`
  - `HighDelayed`
- Deferred close queues:
  - `AsyncCloseList`
  - `DelayedCloseList`
  - `FatCloseItem`
- Shared zero page: `ZeroPage`.

### `FAT_WINDOW`

Represents a window into the FAT free-cluster bitmap when the FAT is too large to keep one full bitmap resident.

Fields:

- `FirstCluster`
- `LastCluster`
- `ClustersFree`

### `CLOSE_CONTEXT`

Carries state for asynchronous or delayed close processing.

Fields:

- Global and per-VCB list links.
- `Vcb`
- `Fcb`
- `TypeOfOpen`
- `Free`

This structure can be embedded/overlaid in a `CCB`.

### `VCB`

Volume Control Block for each mounted FAT volume.

Major categories:

- Common volume file header: `VolumeFileHeader`.
- Global mount linkage: `VcbLinks`.
- Device linkage: `TargetDeviceObject`, `Vpb`, `CurrentDevice`, optional `VolumeGuid`, `VolumeGuidPath`.
- State: `VcbState`, `VcbCondition`.
- Root object: `RootDcb`.
- Allocation metadata:
  - `NumberOfWindows`
  - `Windows`
  - `CurrentWindow`
  - `Bpb`
  - `First0x24BytesOfBootSector`
  - `AllocationSupport`
  - `DirtyFatMcb`
  - `BadBlockMcb`
  - `FreeClusterBitMap`
  - `FreeClusterBitMapMutex`
  - `ChangeBitMapResource`
  - `ClusterHint`
- Open counts:
  - `DirectAccessOpenCount`
  - `OpenFileCount`
  - `ReadOnlyCount`
  - `InternalOpenCount`
  - `ResidualOpenCount`
- Synchronization:
  - `Resource`
  - `DirectoryFileCreationMutex`
  - `AdvancedFcbHeaderMutex`
- Cache/stream objects:
  - `VirtualVolumeFile`
  - `SectionObjectPointers`
  - `VirtualEaFile`
  - `EaFcb`
- Volume locking and notifications:
  - `FileObjectWithVcbLocked`
  - `DirNotifyList`
  - `NotifySync`
- Verification and dirty-clean timers:
  - `VerifyThread`
  - `CleanVolumeDpc`
  - `CleanVolumeTimer`
  - `LastFatMarkVolumeDirtyCall`
- Statistics and tunneling:
  - `Statistics`
  - `Tunnel`
- Media/device details:
  - `ChangeCount`
  - `DeviceNumber`
  - `SwapVpb`
- Per-volume close queues:
  - `AsyncCloseList`
  - `DelayedCloseList`

### `VCB_STATE_*`

Defines volume state flags such as:

- locked
- removable media
- volume dirty
- mounted dirty
- shutdown
- close in progress
- deleted FCB
- create in progress
- boot/paging file
- deferred flush
- async close active
- write protected
- removal prevented
- volume dismounted
- VPB lifecycle flags
- dismount in progress
- bad blocks populated
- hotpluggable
- mount in progress

`VCB_STATE_FLAG_VOLUME_DISMOUNTED` is explicitly documented as FSCTL dismount state, not a replacement for `VcbCondition`.

### `FILE_SYSTEM_STATISTICS`

Combines `FILESYSTEM_STATISTICS` and `FAT_STATISTICS`, padded to a 64-byte multiple to avoid cache-line tearing. `Vcb->Statistics` points to one per processor.

### `VOLUME_DEVICE_OBJECT`

An NT `DEVICE_OBJECT` with FastFAT volume state appended.

Fields:

- Base `DEVICE_OBJECT`.
- Work overflow accounting:
  - `PostedRequestCount`
  - `OverflowQueueCount`
  - `OverflowQueue`
  - `OverflowQueueSpinLock`
- `VolumeFileHeader`
- Embedded `VCB`.

### `FILE_NAME_NODE`

Name index entry used in per-directory splay trees.

Fields:

- Back-pointer to `Fcb`.
- Name union: OEM or Unicode.
- `FileNameDos` marker.
- `RTL_SPLAY_LINKS`.

### `NON_PAGED_FCB`

Nonpaged per-FCB state required by cache/MM and async writes.

Fields:

- `SectionObjectPointers`
- `OutstandingAsyncWrites`
- `OutstandingAsyncEvent`
- `AdvancedFcbHeaderMutex`

### `FCB` / `DCB`

The File Control Block and Directory Control Block share the same structure. `DCB` is typedef’d to `FCB` except when building FSKD extensions.

Major fields:

- `FSRTL_ADVANCED_FCB_HEADER Header`
- `NonPaged`
- `FirstClusterOfFile`
- Parent/volume relationship:
  - `ParentDcbLinks`
  - `ParentDcb`
  - `Vcb`
- State:
  - `FcbState`
  - `FcbCondition`
  - `ShareAccess`
- Open/accounting counters:
  - `UncleanCount`
  - `OpenCount`
  - `NonCachedUncleanCount`
  - `PurgeFailureModeEnableCount`
- On-disk location:
  - `DirentOffsetWithinDirectory`
  - `LfnOffsetWithinDirectory`
- Cached timestamps:
  - `CreationTime`
  - `LastAccessTime`
  - `LastWriteTime`
- Allocation/cache:
  - `ValidDataToDisk`
  - `Mcb`
- Directory-specific union member:
  - `ParentDcbQueue`
  - `DirectoryFileOpenCount`
  - `DirectoryFile`
  - `UnusedDirentVbo`
  - `DeletedDirentHint`
  - `RootOemNode`
  - `RootUnicodeNode`
  - `FreeDirentBitmap`
  - `FreeDirentBitmapBuffer`
- File-specific union member:
  - `FileLock`
  - pre-Win8 `Oplock`
  - `LazyWriteThread`
- Name and attribute state:
  - `EaModificationCount`
  - `ShortName`
  - `FullFileName`
  - `FinalNameLength`
  - `DirentFatFlags`
  - `ExactCaseLongName`
  - `LongName` union for OEM or Unicode LFN tree node
- Move/defrag synchronization:
  - `MoveFileEvent`

The comments explain why FastFAT keeps both OEM and Unicode splay trees: FAT has both OEM short names and Unicode long names on disk, and a single Unicode tree would not reliably preserve the current prefix-lookup assumptions without further duplicate-FCB handling.

### `FCB_STATE_*`

Defines per-file/per-directory state flags:

- delete on close
- truncate on close
- paging file
- force cache miss in progress
- flush FAT
- temporary
- system file
- names in splay tree
- OEM long name present
- Unicode long name present
- delay close
- short-name case flags
- deny defrag
- zero on deallocation

`FCB_LOOKUP_ALLOCATIONSIZE_HINT` is `-1`, meaning allocation size must be discovered from disk.

### `CCB`

Context Control Block allocated per file object/handle.

Important fields:

- Node identity.
- `Flags` plus `ContainsWildCards`.
- Optional encryption-on-close context.
- Union containing either:
  - Directory/query/EA state:
    - `OffsetToStartSearchFrom`
    - OEM query template as wildcard string or constant 8.3 name
    - Unicode query template
    - `EaModificationCount`
    - `OffsetOfNextEaToReturn`
  - `CloseContext` overlay for close processing.

### `CCB_FLAG_*`

Defines handle state such as:

- match all
- skip short-name compare
- free query template buffers
- user-set timestamp fields
- read-only handle
- DASD flush/purge state
- delete on close
- opened by short name
- mixed-case query template
- extended DASD I/O allowed
- match volume ID
- close-context overlay active
- complete dismount
- manage-volume access restriction
- format-unit sent
- deny defrag
- first write seen

### `REPINNED_BCBS`

Tracks BCBs that must remain pinned until IRP completion during abnormal unwinding.

- Fixed array size: `REPINNED_BCBS_ARRAY_SIZE` = 4.
- Chains through `Next` when more BCBs are needed.

### `IRP_CONTEXT`

Per-originating-IRP context used by FSD/FSP paths.

Fields:

- Node identity.
- Work queue item.
- Originating IRP.
- Real device.
- VCB for exception handling.
- Major/minor function.
- `PinCount`.
- Flags controlling wait/write-through/recursive/FSP/user I/O behavior.
- `ExceptionStatus`.
- Noncached I/O context pointer.
- Embedded `REPINNED_BCBS`.

### `IRP_CONTEXT_FLAG_*`

Defines request behavior flags:

- disable dirty
- wait allowed
- write through
- disable write through
- recursive call
- disable popups
- deferred write
- verify read
- stack I/O context
- in FSP
- user I/O
- disable raise
- override verify
- cleanup breaking oplock
- swapped stack on newer NT targets
- parent by child

### `FAT_IO_CONTEXT`

Context for noncached I/O.

Fields:

- Saved IRP context flags.
- Async multi-run IRP count and master IRP.
- Zero MDL for partial-sector zeroing.
- Union:
  - Async state with held resources, request byte count, file object, nonpaged FCB.
  - Sync event.

### Other Helper Structures

- `IO_RUN`: describes one LBO/VBO/offset/byte-count run for multi-run I/O.
- `DELETE_CONTEXT`: stores file size and first cluster for delete/undelete support.
- `DEFERRED_FLUSH_CONTEXT`: timer/DPC/work item for delayed flush.
- `CLEAN_AND_DIRTY_VOLUME_PACKET`: worker packet for clean/dirty volume marking.
- `PAGING_FILE_OVERFLOW_PACKET`: carries paging-file IRP and FCB when stack is low.
- `EA_RANGE`: pins and describes a range of EA data using an inline BCB array with fallback chain.
- `CLUSTER_TYPE`: classification of FAT cluster entries:
  - available
  - reserved
  - bad
  - last
  - next
- `FAT_CALLOUT_PARAMETERS`: Windows Threshold stack-swapping callout parameters for create handling.

## Research Notes

`fatstruc.h` is the structural backbone of FastFAT. It captures the driver’s object hierarchy:

`FAT_DATA` -> mounted `VCB`s -> tree of `FCB`/`DCB` objects -> per-handle `CCB`s -> per-request `IRP_CONTEXT`s.

The file also documents key architectural constraints: FAT’s 32-bit allocation model, mixed OEM/Unicode name lookup, cache/MM section-object requirements, close deferral, volume dirty tracking, and the split between paged object state and nonpaged state required for kernel callbacks.
