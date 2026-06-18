# File Research: sources/windows/windows-driver-samples/filesys/fastfat/strucsup.c

## Role

`strucsup.c` is FastFAT’s in-memory structure support layer. It creates, initializes, links, traverses, tears down, and frees the main runtime objects: `VCB`, `FCB`, `DCB`, `CCB`, nonpaged FCB extensions, resources, IRP contexts, close contexts, directory free-entry bitmaps, and volume stream file objects.

## Key Routines

- `FatInitializeVcb`: builds a mounted volume control block, references the target device, queries hotplug/removable state, initializes cache maps, dirty/bad cluster MCBs, notify state, statistics, VPB swap storage, close queues, and the virtual volume file.
- `FatTearDownVcb` / `FatDeleteVcb`: remove internal opens, uninitialize cache maps, delete root/EA structures, free VPBs, MCBs, statistics, tunnel cache, resources, and device references.
- `FatCreateRootDcb`, `FatCreateFcb`, `FatCreateDcb`: allocate and initialize root directory, file, and subdirectory control blocks, including resources, MCBs, timestamps, names, oplocks, locks, parent-child links, and allocation hints.
- `FatDeleteFcb`: validates zero open count, tears down oplocks/file locks/per-stream contexts/MCBs/name buffers/resources/nonpaged state, and unlinks from parent trees.
- `FatCreateCcb`, `FatDeleteCcb`, `FatDeallocateCcbStrings`: manage per-handle context records and query template buffers.
- `FatCreateIrpContext`, `FatDeleteIrpContext_Real`: construct and free request context state, including major/minor operation, target VCB/device, write-through state, recursive-call marking, and optional I/O context cleanup.
- `FatGetNextFcbBottomUp`, `FatGetNextFcbTopDown`: enumerate FCB/DCB trees in lock-order-sensitive ways.
- `FatSwapVpb`, `FatCheckForDismount`: detach a mounted VPB, process dismount eligibility, tear down internal opens, process delayed closes, and delete the volume device when reference counts reach zero.
- `FatConstructNamesInFcb`: builds short, OEM long, or Unicode long name representations and inserts them into parent directory splay trees.
- `FatCheckFreeDirentBitmap`: grows a directory’s free-dirent bitmap as allocation grows.
- `FatAllocateCloseContext`, `FatPreallocateCloseContext`: manage global preallocated close contexts via an interlocked SList.
- `FatEnsureStringBufferEnough`, `FatFreeStringBuffer`: utility allocation/free helpers for string buffers, avoiding freeing stack-backed buffers.
- `FatScanForDataTrack`: reads CD-ROM TOC data and allows FastFAT mounting only when media looks like a single data track, with special fallback for PD media failures.

## Important Mechanics

The file is defensive about partial initialization. Most complex creation paths track unwind resources and use `try/finally` to free partially initialized state on abnormal termination. VCB setup is especially careful because it has to balance global VCB list insertion, target device references, cache-map initialization, close-context preallocation, and VPB fallback allocation.

Directory child ordering is deliberate: DCBs are inserted at the head and FCBs at the tail of `ParentDcbQueue`, allowing child directories to be enumerated before child files for bottom-up locking and teardown.

Name construction contains nuanced FAT long-name handling. ASCII-only long names can be represented in uppercase OEM form and inserted into the OEM prefix tree. Extended Unicode names are kept in the Unicode prefix tree to avoid collisions caused by best-fit OEM mappings.

## Dependencies And Coupling

This file depends heavily on Windows kernel filesystem primitives: `ERESOURCE`, `FsRtl` advanced headers, notify sync, tunnel cache, oplocks, file locks, cache manager callbacks, VPBs, stream file objects, large MCBs, and device I/O controls. It is central to mount, create, close, verify, cleanup, dismount, and prefix lookup behavior across the FastFAT driver.
