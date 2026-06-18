# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4layouts.c

Purpose: implements NFSD pNFS layout state management, device ID mapping, layout grant/return bookkeeping, layout recall callbacks, and fencing behavior for layout-capable exports.

Key structures and state:
- `struct nfs4_layout` records one granted layout segment and links it to a layout stateid.
- `struct nfs4_layout_stateid` objects are allocated from `nfs4_layout_stateid_cache` and track per-client/per-file layout state, granted segments, recall callback, lease, fencing work, and layout type.
- `nfsd4_layout_ops[]` dispatches layout-type-specific operations for flexfile, block, and SCSI layouts depending on config.
- Device IDs are mapped to export fsids by `struct nfsd4_deviceid_map` entries in an RCU-protected hash table guarded by `nfsd_devid_lock`.

Major logic:
- `nfsd4_setup_layout_type()` enables export layout types based on export flags and filesystem export operations.
- `nfsd4_set_deviceid()` allocates or reuses an export fsid-to-device-ID mapping and stores generation data in the protocol deviceid.
- `nfsd4_alloc_layout_stateid()` creates a layout stateid from an open/lock/delegation stateid, finds an associated `nfsd_file`, installs a layout lease unless recalls are disabled, and links the state to client and file lists.
- `nfsd4_preprocess_layout_stateid()` validates layout stateids, creates one if allowed, checks filehandle match, layout type consistency, and stateid generation ordering.
- Segment helpers compute layout end offsets, merge compatible adjacent/overlapping segments, detect overlap, and update lengths safely with `NFS4_MAX_UINT64`.
- `nfsd4_insert_layout()` recalls conflicting layout states for other clients, merges or allocates a segment, and updates the layout stateid returned to the client.
- Layout return paths handle file-specific, fsid, all-client, all-file, and all-client cleanup by moving segments to reap lists and dropping stateid references.
- Recall logic uses `nfsd4_recall_file_layout()` to mark a layout recalled, increment file recall counters, and run `CB_LAYOUTRECALL`.
- Recall completion polls for layout return until two lease periods, then fences the client using layout driver support or `/sbin/nfsd-recall-failed`.
- Lease manager hooks convert VFS lease breaks into layout recalls and schedule fencing on timeout.

Concurrency and lifetime:
- Client layout lists are protected by `cl_lock`; file layout lists by `fi_lock`; per-layout segment lists by `ls_lock`; stateid operations serialize with `ls_mutex`.
- Layout segments hold references on their layout stateids and are freed via reap lists outside lock-heavy paths.
- Delayed fencing work holds a stateid reference while it runs and re-arms itself to prevent duplicate timeout references.
- Layout stateid freeing cancels pending fence work, unlinks from client/file lists, closes the layout lease, adjusts recall counters, and frees cache memory.

Important dependencies:
- Uses callback infrastructure from `nfs4callback.c` for `CB_LAYOUTRECALL`.
- Uses VFS lease APIs (`kernel_setlease`, `lease_modify`) to integrate pNFS recalls with local file access conflicts.
- Delegates layout-type-specific behavior to `proc_getdeviceinfo`, `proc_layoutget`, `proc_layoutcommit`, and optional `fence_client`.

Risk/edge cases:
- Split layout returns are not supported; the code retains the whole segment when a return would split it.
- Fencing retries indefinitely with exponential backoff to avoid data corruption if client fencing fails.
- Device ID mappings are freed at pNFS exit without RCU grace waiting in this file; callers must respect module/global teardown assumptions.
- Layout conflict handling recalls all other layout states on the same file before granting a new layout.
