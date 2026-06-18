# File Research: sources/windows/reactos/drivers/filesystems/fastfat/strucsup.c

This file implements FastFAT in-memory structure allocation, initialization, teardown, traversal, dismount, name-node construction, directory free-dirent bitmap management, close-context pooling, dynamic string buffers, and CD data-track probing.

Key responsibilities:
- Allocate/free CCBs, FCBs, nonpaged FCB extensions, ERESOURCEs, and IRP contexts.
- Initialize VCBs during mount, including target-device references, hotplug/deferred-flush flags, stream file objects, cache maps, MCBs, VPB swap storage, statistics, close queues, and advanced FCB headers.
- Tear down and delete VCBs, including internal stream files, EA file, root DCB tree, notification sync, allocation support, MCBs, timers, tunnel cache, target-device references, and VPBs.
- Create root DCBs, regular FCBs, and directory DCBs from FAT dirents.
- Delete FCB/DCB/root DCB records and their locks, oplocks, file locks, names, MCBs, directory bitmaps, per-stream contexts, and child links.
- Create/delete CCBs and their query-template strings.
- Create/delete IRP contexts and attached `FAT_IO_CONTEXT` state.
- Enumerate FCB trees bottom-up or top-down for lock ordering and teardown.
- Swap VPBs and check whether a volume can be dismounted/deleted.
- Construct short/long name nodes in FCBs and insert them into parent splay trees.
- Grow free-dirent bitmaps as directory allocation grows.
- Check whether all user handles are closed.
- Preallocate and consume close contexts from the global SList.
- Manage reusable string buffers safely across stack/pool buffers.
- Read CD-ROM TOC data to avoid mounting audio-only media as FAT.

Important functions:
- `FatInitializeVcb`: mount-time VCB initialization with extensive abnormal-unwind cleanup.
- `FatTearDownVcb`: closes internal stream/cache objects and marks the VCB bad.
- `FatDeleteVcb`: removes a VCB from global state and frees all subordinate structures.
- `FatCreateRootDcb`: builds the root directory object, with FAT12/16 fixed-root mapping or FAT32 cluster-chain lookup.
- `FatCreateFcb`: builds a file FCB, including timestamps, allocation hints, file lock, oplock, MCB, resources, and names.
- `FatCreateDcb`: builds a directory DCB, including child queue, bitmap state, resources, MCB, oplock, and names.
- `FatDeleteFcb`: deletes file or directory objects once open count reaches zero.
- `FatCreateCcb`, `FatDeallocateCcbStrings`, `FatDeleteCcb`: CCB lifetime helpers.
- `FatCreateIrpContext`, `FatDeleteIrpContext_Real`: IRP-context lifetime helpers.
- `FatGetNextFcbBottomUp`, `FatGetNextFcbTopDown`: tree traversal helpers for lock acquisition and teardown.
- `FatSwapVpb`: replaces the mounted VPB with the saved spare VPB during forced disconnect.
- `FatCheckForDismount`: checks VPB/open counts, tears down internal opens, drains closes, deletes the volume device when possible, or swaps VPB on force.
- `FatConstructNamesInFcb`: builds short and long name nodes, chooses OEM vs Unicode LFN prefix storage, and inserts names into splay trees.
- `FatCheckFreeDirentBitmap`: grows a directory’s free-dirent bitmap under the directory-file mutex.
- `FatIsHandleCountZero`: walks the tree to determine whether user handle counts are gone.
- `FatAllocateCloseContext`, `FatPreallocateCloseContext`: close-context SList helpers.
- `FatEnsureStringBufferEnough`, `FatFreeStringBuffer`: dynamic string buffer helpers.
- `FatScanForDataTrack`: reads CD TOC and returns true only for a single data track or PD-media special failures.

Notable behavior and risks:
- VCB initialization has many partial-allocation unwind paths; leaked close context balancing is handled specially when stream file creation fails.
- Root DCB allocation uses nonpaged pool, while ordinary FCB/DCB allocation uses paged pool except for paging files.
- Directory DCBs are inserted at the head and file FCBs at the tail so child directories precede files for bottom-up lock-order traversal.
- `FatCheckForDismount` depends on VPB reference counts matching residual/internal opens and may either delete the volume device or only disconnect it.
- Unicode LFN prefix storage is conservative: extended-character LFNs are generally kept in Unicode to avoid OEM best-fit collisions.
- `FatFreeStringBuffer` detects stack-backed buffers via `IoGetStackLimits` and only frees non-stack buffers.
