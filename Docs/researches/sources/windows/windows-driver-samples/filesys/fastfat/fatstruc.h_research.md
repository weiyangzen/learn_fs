# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fatstruc.h

## Purpose

`fatstruc.h` defines the major in-memory data structures for the Windows Driver Samples FastFAT filesystem driver. It describes global driver state, mounted-volume state, file/directory control blocks, per-handle context, IRP context, noncached I/O context, deferred work packets, EA ranges, volume statistics, and conditional stack-swapping callout parameters.

The header is structural glue for the driver: implementation files rely on these layouts for locking, cache manager integration, allocation tracking, name lookup, close processing, verification, extended attributes, file IDs, and dispatch exception unwinding.

## Core Structures

- `FAT_DATA`
  - Global nonpaged driver record with node type/size, mounted VCB queue, driver object, disk/CDROM filesystem device objects, global resource, process pointer for cache manager use, processor count, mode/feature flags, deferred close lists/counters, close work item, a general spin lock, cache manager callbacks, no-op callbacks, and a zero page.
  - Flags record Chicago extensions, Fujitsu FMR behavior, async close activity, shutdown, code-page invariance, and aggressive close-queue draining.
- `FAT_WINDOW`
  - Per-window allocation summary with first cluster, last cluster, and free cluster count. VCBs use windows when a single free-cluster bitmap would be too large.
- `CLOSE_CONTEXT`
  - Deferred close state embedded in a CCB to avoid extra close-path allocation. Carries global/VCB list links, VCB, FCB, open type, and a `Free` marker.
- `VCB`
  - Mounted-volume control block. It contains a volume file `FSRTL_ADVANCED_FCB_HEADER`, VCB list links, target device object, volume GUID/path, VPB, VCB state/condition, root DCB, FAT windowing data, direct/open/read-only/internal/residual open counts, unpacked BPB, saved boot-sector bytes, allocation support data, dirty FAT MCB, bad-block MCB, free-cluster bitmap and mutex, resources, virtual volume file, section object pointers, cluster hint, current device, EA file object/FCB, lock owner file object, notify list/sync, directory stream file mutex, verify thread, clean-volume timer/DPC, last dirty-mark time, per-processor statistics, tunnel cache, media change count, device number, swap VPB, per-volume close queues, advanced FCB header mutex, and debug-only close-context count.
  - `AllocationSupport` caches root directory LBO, file area LBO, root directory byte size, cluster count, free cluster count, FAT index bit size, and log2 byte/cluster geometry.
- `FILE_SYSTEM_STATISTICS`
  - A padded per-processor statistics record combining `FILESYSTEM_STATISTICS` and `FAT_STATISTICS`, rounded to a 64-byte multiple to avoid cache-line tearing.
- `VOLUME_DEVICE_OBJECT`
  - A device object with per-volume work queue/overflow tracking, spin lock, volume file common header, and embedded `VCB`.
- `FILE_NAME_NODE`
  - Name tree node linking an FCB to either an OEM or Unicode name, marking whether the opened name is DOS/short-name style, and embedding splay links.
- `NON_PAGED_FCB`
  - Nonpaged stream fields for section object pointers, async noncached valid-data extending write count, completion event, and advanced FCB header mutex.
- `FCB` / `DCB`
  - Shared file/directory control block layout with `FSRTL_ADVANCED_FCB_HEADER`, nonpaged FCB pointer, first cluster, parent links, parent DCB, VCB, state, condition, share access, open/cleanup counts, noncached cleanup count, purge failure count, dirent and LFN offsets, cached timestamps, valid-data-to-disk, allocation MCB, and a union for directory-specific versus file-specific state.
  - Directory-specific state includes child queue, directory stream open count/file object, unused/deleted dirent hints, OEM and Unicode splay roots, free-dirent bitmap, and initial bitmap buffer.
  - File-specific state includes byte-range `FILE_LOCK`, pre-Win8 `OPLOCK`, and lazy-writer thread marker.
  - Common tail fields include EA modification count, short name, full file name, final name length, cached FAT attribute byte, exact-case long name, optional OEM/Unicode long-name tree node, and move-file event.
- `CCB`
  - Per-file-object context with node type/size, 24-bit flags, wildcard marker, encryption-on-close context, and a union between active open state and embedded `CLOSE_CONTEXT`.
  - Active open state tracks directory query resume offset, OEM query template as wildcard string or constant 8.3 value, Unicode query template, EA modification count, and next EA offset.
- `REPINNED_BCBS` and `IRP_CONTEXT`
  - Repinned BCB chains preserve cache pins during abnormal termination unwinding.
  - IRP context stores node metadata, worker item, originating IRP, real device, VCB, major/minor function, pin count, flags, exception status, noncached I/O context, and inline repinned BCB storage.
- `FAT_IO_CONTEXT`
  - Noncached I/O helper preserving IRP context flags, master IRP and outstanding IRP count for multi-run I/O, zeroing MDL, and either async resource/file/nonpaged-FCB metadata or a sync event.
- `IO_RUN`
  - One physical run for multi-run I/O: LBO, VBO, user-buffer offset, byte count, and saved partial IRP.
- `DELETE_CONTEXT`
  - File size and first cluster saved during dirent deletion so undelete tools can recover metadata.
- `DEFERRED_FLUSH_CONTEXT`, `CLEAN_AND_DIRTY_VOLUME_PACKET`, and `PAGING_FILE_OVERFLOW_PACKET`
  - Work/timer/DPC packets for delayed flush, clean/dirty volume work, and low-stack paging file I/O handling.
- `EA_RANGE`
  - Pinned EA file range with data pointer, starting VBO, length, BCB chain length, auxiliary-buffer marker, dynamic BCB chain pointer, and inline BCB array.
- `FAT_CALLOUT_PARAMETERS`
  - Windows Threshold and later stack-swapping parameter block, currently carrying create-path parameters plus IRP and exception statuses.

## State Flags and Enums

- `VCB_CONDITION`: `VcbGood`, `VcbNotMounted`, `VcbBad`.
- VCB state flags cover lock/removable/dirty/mounted-dirty/shutdown/close/create/paging-file/deferred-flush/async-close/write-protected/removal-prevented/dismounted/VPB/discard/dismount/bad-block/hotplug/mount states.
- `FCB_CONDITION`: `FcbGood`, `FcbBad`, `FcbNeedsToBeVerified`.
- FCB state flags cover delete-on-close, truncate-on-close, paging file, force-cache-miss, flush-FAT, temporary, system file, splay-tree presence, OEM/Unicode long name presence, delayed close, short-name case preservation, defrag denial, and zero-on-deallocation.
- CCB flags cover wildcard/query behavior, template buffer ownership, user-set times, read-only handles, DASD flush/purge, delete-on-close, short-name open, mixed-case query template, extended DASD I/O, volume-label matching, close-context conversion, complete dismount, manage-volume restrictions, format unit handling, defrag denial, and first-write tracking.
- IRP context flags cover dirty disable, wait, write-through, write-through disable, recursive call, popup disable, deferred write, verify read, stack I/O context, FSP execution, user I/O, disable raise, override verify, cleanup breaking oplock, Threshold stack swapping, and parent-by-child ownership.
- `CLUSTER_TYPE`: available, reserved, bad, last, or next cluster.

## Key Layout and Behavior Notes

- VCB and FAT data records must be allocated from nonpaged pool.
- `PBCB` is typedefed as `PVOID` because BCBs are cache-manager objects.
- VCB's dirty FAT tracking uses an MCB where holes mean clean sectors and `LBO == VBO` runs mean dirty sectors.
- The free cluster bitmap uses `1` for occupied clusters and `0` for free clusters.
- `InternalOpenCount` and `ResidualOpenCount` are volatile because internal stream/root/EA opens are tracked concurrently.
- `VolumeFileHeader`, FCB headers, `SectionObjectPointers`, and nonpaged FCB fields connect FastFAT objects to the cache manager and memory manager.
- DCBs keep two name splay trees, OEM and Unicode, because FAT can expose both short OEM and long Unicode names and not every Unicode name maps uniquely or representably through the OEM code page.
- `EaModificationCount` is intentionally fixed after the file/directory union because DCB slack-space calculations depend on its offset.
- `DCB_UNION_SLACK_SPACE` computes unused directory-union storage for the initial free-dirent bitmap buffer.
- `FCB_LOOKUP_ALLOCATIONSIZE_HINT` is the sentinel `-1` allocation size meaning the real allocation must be discovered from the FAT.
- The CCB overlays close context over query/EA enumeration state once a handle is converted into delayed/asynchronous close processing.
- `EA_RANGE` has an inline BCB array of eight entries and can switch to a separate chain/auxiliary buffer for larger or noncontiguous EA ranges.
- Statistics are padded to a cache-line multiple to reduce false sharing across per-processor counters.

## Integration

These structures are consumed by the declarations in `fatprocs.h` and by the FastFAT implementation modules:
- Allocation code updates VCB allocation support, FAT windows, dirty FAT MCB, free cluster bitmap, and FCB MCBs.
- Cache/device I/O code uses VCB virtual volume files, FCB/VCB section object pointers, nonpaged FCB fields, `FAT_IO_CONTEXT`, `IO_RUN`, and BCB tracking.
- Create/name/path lookup code uses DCB child queues, OEM/Unicode splay roots, short/long name nodes, full names, and dirent offsets.
- Cleanup/close code uses FCB/VCB open counts, CCB flags, close context overlays, and global/per-volume deferred close lists.
- EA code uses VCB `VirtualEaFile`/`EaFcb`, FCB/CCB EA modification counts, and `EA_RANGE`.
- Verification and dismount code use VCB/FCB condition fields, state flags, verify thread, VPB fields, direct access counts, and root/child FCB hierarchy.
- Notification and tunneling code use VCB notify/tunnel fields and FCB full-name/final-name state.

## Notable Risks and Review Points

- Layout sensitivity is high. Comments explicitly warn not to move `EaModificationCount`, and several structures are tuned for pool size or cache-line behavior.
- CCB uses bitfields and a union overlay, so code must not read query/EA state after `CCB_FLAG_CLOSE_CONTEXT` conversion.
- Several counts are plain `CLONG` or `ULONG` while some are volatile; callers must use the expected locks/spin locks/resources around nonvolatile fields.
- Dual OEM/Unicode splay trees are correctness-critical. Missing an open FCB during prefix lookup can create duplicate FCBs and is treated as a serious invariant failure elsewhere.
- VCB state flags and `VcbCondition` are distinct. `VCB_STATE_FLAG_VOLUME_DISMOUNTED` records an FSCTL dismount and does not replace the volume validity condition.
- `FAT_IO_CONTEXT` async state stores resources/thread IDs for completion-time release; incorrect initialization can leak locks or complete I/O while resources are still owned.
- Several fields exist for legacy or conditional behavior (`SYSCACHE_COMPILE`, pre-Win8 oplock storage, Threshold stack swapping), so cross-version builds can have meaningfully different layouts.
