# File Research: sources/os/linux/linux/fs/nfsd/nfs4layouts.c

This file implements NFSD pNFS layout state management. It tracks device ID mappings, layout stateids, granted layout segments, layout recalls, lease integration, and fencing behavior when clients do not return recalled layouts.

Primary responsibilities:
- Maintain a global pNFS device-id-to-export-fsid map.
- Determine which pNFS layout types an export supports.
- Allocate, validate, and free layout stateids.
- Insert, merge, return, and free layout segments for a stateid/client/file.
- Recall conflicting layouts and schedule callback work.
- Integrate layout state with kernel file leases so local file access can trigger layout recall.
- Fence clients when layout recall times out and the layout driver supports fencing.
- Initialize/destroy pNFS layout slab caches and device-id maps.

Important entry points and exports:
- `nfsd4_init_pnfs()` initializes device hash buckets and slab caches.
- `nfsd4_exit_pnfs()` destroys slab caches and frees device-id maps.
- `nfsd4_setup_layout_type()` sets per-export supported layout type bits based on config and exportfs block layout capabilities.
- `nfsd4_set_deviceid()` assigns a device id for an export/device generation.
- `nfsd4_find_devid_map()` looks up a device-id map by index.
- `nfsd4_preprocess_layout_stateid()` validates an existing layout stateid or creates one from open/lock/delegation state.
- `nfsd4_insert_layout()` records a newly granted layout segment and updates the layout stateid generation.
- `nfsd4_return_file_layouts()`, `nfsd4_return_client_layouts()`, `nfsd4_return_all_client_layouts()`, and `nfsd4_return_all_file_layouts()` process explicit or forced layout returns.
- `nfsd4_close_layout()` tears down the lease/file reference associated with a layout stateid.

Core data structures:
- `struct nfs4_layout` represents one granted layout segment attached to a layout stateid.
- `struct nfs4_layout_stateid` is allocated through the generic NFSv4 stateid allocator and tracks layouts per client and per file.
- `nfsd4_layout_ops[]` dispatches layout-type-specific behavior for flex-files, block, and SCSI layouts when enabled.
- `nfsd4_deviceid_map` ties a generated fsid index to export fsid bytes.

Control flow:
- `LAYOUTGET` processing in `nfs4proc.c` calls `nfsd4_preprocess_layout_stateid()`, then layout-type driver `proc_layoutget()`, then `nfsd4_insert_layout()`.
- On insertion, this file recalls conflicting layouts from other layout stateids on the same file before recording a new segment.
- Segment insertion attempts to merge adjacent/overlapping segments with identical iomode; otherwise allocates a new `nfs4_layout`.
- `LAYOUTRETURN` can return file, fsid, or all layouts. File returns may shrink or remove segments; split returns are not fully supported and retain the whole segment.
- Recall uses `nfsd4_recall_file_layout()` to mark a stateid recalled, increment per-file recall count, take a stateid reference, and run `CB_LAYOUTRECALL`.
- Callback completion frees returned layouts or fences the client if recall does not complete.
- Lease break callbacks trigger layout recall and may schedule fencing on timeout.

State and synchronization:
- `nfsd_devid_lock` protects global device-id map creation and sequence allocation; lookups use RCU list traversal.
- `cl_lock` protects client layout state lists.
- `fi_lock` protects per-file layout state lists and conflict checks.
- `ls_lock` protects a layout stateid’s layout segment list, recalled/fenced flags, and fence work checks.
- `ls_mutex` serializes layout operation processing on a layout stateid.
- Layout segment references hold a stateid reference; freeing segments drops those references.
- Delayed fence work takes an extra stateid reference while running.

Dependencies and integration:
- Uses layout-type operations from `pnfs.h`: flex-files, block, SCSI.
- Uses NFSv4 callback framework from `nfs4callback.c` for `CB_LAYOUTRECALL`.
- Uses kernel lease infrastructure through `lease_manager_operations`.
- Uses exportfs layout capability helpers for block layout support.
- Uses usermode helper `/sbin/nfsd-recall-failed` as fallback fencing notification when driver-specific fencing is absent.
- Emits pNFS tracepoints for allocation, recall, return, unhash, and failure cases.

Error handling and notable risks:
- Fencing retries indefinitely with exponential backoff up to `MAX_FENCE_DELAY` to avoid data corruption; administrator intervention may be required.
- Lease timeout handling carefully avoids duplicate fence-worker references by checking delayed-work state and rearming pending work.
- Layout return split handling is intentionally limited; a middle split logs and retains the full segment.
- `BUG_ON` assertions enforce assumptions such as successful file association and lease unlock arguments.
- Device-id maps are global and freed at pNFS shutdown; export `ex_devid_map` sharing relies on stable fsid matching.
- Recall conflict returns `nfserr_recallconflict` after initiating recalls of other layout stateids.
