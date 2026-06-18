# File Research: sources/windows/reactos/drivers/filesystems/cdfs/strucsup.c

Implements CDFS in-memory structure creation, initialization, lookup, teardown, and deletion for VCBs, FCBs, CCBs, IRP contexts, FCB tables, and audio-CD TOC metadata.

Key entry points:
- `CdInitializeVcb()` zeros and initializes a VCB, resources, notification state, swap VPB, target-device reference, FCB table, TOC fields, removable/audio flags, block factor, and media-change count.
- `CdUpdateVcbFromVolDescriptor()` completes mount-time VCB initialization from an ISO/Joliet volume descriptor or creates pseudo structures for audio disks.
- `CdDeleteVcb()` frees VCB-owned auxiliary state, resources, TOC, notify state, target reference, VPBs, and deletes the containing volume device object.
- `CdCreateFcb()` looks up or allocates an FCB by file ID and node type, initializes common fields, MCB, nonpaged FCB, advanced header, and oplock state for data FCBs.
- `CdInitializeFcbFromPathEntry()` initializes a directory/index FCB from a path-table entry.
- `CdInitializeFcbFromFileContext()` initializes a file/data FCB from one or more directory extents and loads its allocation map.
- `CdCreateCcb()` and `CdDeleteCcb()` allocate/free per-open context structures.
- `CdCreateFileLock()` lazily attaches an FsRtl file-lock object to a data FCB.
- `CdCreateIrpContext()`, `CdCleanupIrpContext()`, and `CdInitializeStackIrpContext()` manage request contexts and the private lookaside list.
- `CdTeardownStructures()` walks from an FCB toward the root, removing unreferenced FCBs from parent queues, prefix trees, and the FCB table.
- `CdLookupFcbTable()` and `CdGetNextFcb()` access the generic-table index by `FILE_ID`.
- `CdProcessToc()` reads and normalizes CD-ROM TOC data, with fallback from `IOCTL_CDROM_READ_TOC_EX` to `IOCTL_CDROM_READ_TOC`.
- `CdTocSerial()` computes an audio-disk serial number from TOC track addresses.

Core mechanics:
- A generic table maps `FILE_ID` values to FCBs using `CdFcbTableCompare()`.
- Mount initialization creates internal stream FCBs for the path table, root directory, and volume DASD file.
- ISO/Joliet mounts reject block sizes other than `SECTOR_SIZE`.
- The path-table FCB is backed by the on-disk path-table extent; the root directory FCB is initialized from a pseudo path entry built from the root dirent.
- The DASD FCB maps the full logical volume and is marked read-only.
- Audio-only disks are exposed through pseudo ISO-like structures: a synthetic path table, root directory entries for tracks, an audio label, and a TOC-derived serial number.
- File FCB initialization walks multi-extent dirents until the final extent and adds each allocation into the FCB MCB.
- Teardown deletes internal stream file objects for index/path-table FCBs once user references reach zero, then removes unreferenced FCBs bottom-up.

Important invariants:
- VCB initialization keeps residual references so the VCB cannot vanish during mount/error cleanup.
- Internal FCBs hold VCB references until dismount removes them.
- FCBs must leave the FCB table before deletion if `FCB_STATE_IN_FCB_TABLE` is set.
- Directory/index FCBs must have empty child queues and no stream file object when deleted.
- `CdTeardownStructures()` uses a top-level teardown flag to avoid recursive teardown.
- `CdCleanupIrpContext()` distinguishes normal deletion, posting, retry, stack contexts, allocated I/O contexts, and lookaside reuse.

Filesystem relevance:
- This is the structural backbone for CDFS mount, open, close, cached I/O, directory hierarchy, and dismount behavior.
- It connects on-disk ISO/Joliet descriptors and CD-ROM TOC data to the runtime VCB/FCB model.

Notable risks:
- Mount and dismount paths depend on precise VCB, VPB, internal-stream, and target-device reference accounting.
- The audio-disk pseudo filesystem path has separate size/label/serial behavior and does not permit raw reads through the zero-sized DASD FCB.
- `CdProcessToc()` mutates the returned TOC for mixed CD+ media by hiding the data track after lead-in audio.
