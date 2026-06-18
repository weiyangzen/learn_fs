# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/ext2fs.h

This is the central Ext2Fsd/ReactOS ext2 driver header. It pulls in NT kernel/WDK definitions plus Linux-derived ext2/ext3/ext4 format headers, defines driver-wide constants, object types, core control blocks, mount flags, memory accounting helpers, and nearly all cross-module function prototypes.

Major definitions:
- Driver identity and options: `EXT2FSD_VERSION`, `DRIVER_NAME`, device names, registry value names, unload/write/preallocation toggles.
- Filesystem layout aliases: `EXT2_SUPER_BLOCK`, `EXT2_INODE`, `EXT2_GROUP_DESC`, `EXT2_DIR_ENTRY`, block/inode/group size macros, and ext3/ext4 count helpers.
- POSIX mode bits and permission helpers used to translate ext inode modes into Windows access and attributes.
- Pool tags, bugcheck codes, debug levels, trace macros, and memory/IRP accounting hooks.

Core structures:
- `EXT2_GLOBAL`: global driver state, fast I/O/filter/cache callbacks, device objects, mounted VCB list, reaper threads, lookaside lists, codepage and hiding-pattern settings, registry path, and performance counters.
- `EXT2_VCB`: mounted volume state, resources, FCB/MCB lists, volume/device objects, geometry, superblock, block/inode sizing, Linux `block_device`/`super_block`/`ext3_sb_info` shims, and max-file-size limits.
- `EXT2_FCB`: per-open-file control state, cache manager header/resources, section objects, locks, oplock, inode pointer, VCB pointer, MCB pointer, and reference/open counters.
- `EXT2_MCB`: metadata/name tree node containing path names, attributes, timestamps, extents, cached inode, dentry pointer, parent/child/target relationships, and reference count.
- `EXT2_CCB`: per-handle context with search pattern, symlink context, Linux-style `struct file`, and EA iteration index.
- `EXT2_IRP_CONTEXT`: per-request dispatch context with IRP, major/minor function, device/file object, FCB/CCB, wait/defer flags, and exception state.
- `EXT2_EXTENT` and `EXT2_RW_CONTEXT`: block I/O extent chains and async read/write tracking.

Functional surface:
- Declares the full driver API for access checks, disk I/O, cleanup/close, cache callbacks, create/link/symlink lookup, debug/devctl/dirctl/dispatch, EA operations, exception handling, indirect/extents block mapping, superblock/group/inode/block load-save, allocation/freeing, htree directory logic, init/unload, Linux shim lifecycle, byte-range locks, memory/object lifecycle, MCB/VCB tree operations, bitmap consistency, NLS conversion, PnP, read/write, journal recovery, shutdown, and volume information.
- Provides inline ext3 64-bit superblock count accessors and prototypes for ext4 group descriptor helpers.
- Defines Windows-specific write gating through `CanIWrite`, with global ext3 force-write and VCB force-write/read-only flags.

Notable risks:
- This header is very broad and tightly couples nearly every module, so signature drift or macro changes have wide blast radius.
- Several portability branches distinguish ReactOS, GNU NTIFS, Win2K, MSVC, and clang-cl; build behavior can vary by compiler target.
- `CanExt2Wait(IRP)` expands to `IoIsOperationSynchronous(Irp)` and references `Irp` rather than the macro parameter name.
- `S_ISFIL` references `S_IFFIL`, which is not defined in this header.
