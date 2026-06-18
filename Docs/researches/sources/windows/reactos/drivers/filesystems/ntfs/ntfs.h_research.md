# File Research: sources/windows/reactos/drivers/filesystems/ntfs/ntfs.h

## Purpose

`ntfs.h` is the central private header for the ReactOS NTFS driver. It defines on-disk NTFS structures, in-memory VCB/FCB/CCB/global/IRP-context structures, constants, tags, helper macros, inline queue marking, and cross-module prototypes.

## Major Definitions

### Driver and Allocation Constants

- Pool tags: `TAG_NTFS`, `TAG_CCB`, `TAG_FCB`, `TAG_IRP_CTXT`, `TAG_ATT_CTXT`, `TAG_FILE_REC`.
- Rounding helpers: `ROUND_UP`, `ROUND_DOWN`.
- Device name: `\Ntfs`.
- File-record and data-run alignment constants:
  - `ATTR_RECORD_ALIGNMENT`
  - `DATA_RUN_ALIGNMENT`
  - `VALUE_OFFSET_ALIGNMENT`.

### Boot and Volume Structures

- `BIOS_PARAMETERS_BLOCK`
- `EXTENDED_BIOS_PARAMETERS_BLOCK`
- `BOOT_SECTOR`
- `NTFS_INFO`

These capture NTFS boot-sector geometry, MFT/MFTMirr locations, cluster and record sizes, volume label, version, flags, and MFT-zone reservation.

### In-Memory Driver State

`DEVICE_EXTENSION` / `NTFS_VCB`

- Contains volume resource state, FCB list, VPB/storage device pointers, stream file object, `$MFT` context and record, volume FCB, parsed NTFS info, file-record lookaside list, MFT data offset, flags, and open-handle count.

`NTFS_GLOBAL_DATA`

- Stores global driver identity, resource, driver/device object pointers, cache callbacks, fast-I/O dispatch table, lookaside lists, and global experimental write-support flag.

`NTFS_CCB`

- Per-open context with directory enumeration state and search pattern.

`NTFS_FCB`

- Per-file state with `FSRTL_COMMON_FCB_HEADER`, section pointers, stream name, path/object names, paging/main resources, parent link, list entry, ref/open counts, flags, MFT index, link count, and cached filename attribute.

`NTFS_IRP_CONTEXT`

- Per-request dispatch state, including IRP, stack location, major/minor function, wait/queue flags, top-level state, target device/file object, saved exception status, and priority boost.

`NTFS_ATTR_CONTEXT`

- Per-attribute state with cached data-run position fields, `LARGE_MCB`, owning file MFT index fields, and copied `NTFS_ATTR_RECORD`.

### On-Disk NTFS Structures

- Attribute type enum covering standard NTFS attributes from `$STANDARD_INFORMATION` through `$LOGGED_UTILITY_STREAM`.
- System file numbers: `$MFT`, `$MFTMirr`, `$LogFile`, `$Volume`, `$AttrDef`, root, `$Bitmap`, `$Boot`, `$BadClus`, `$Quota`, `$UpCase`, `$Extend`.
- File reference mask `NTFS_MFT_MASK`.
- Collation constants and index flags.
- File-name namespace constants.
- NTFS file-attribute flags.
- `NTFS_RECORD_HEADER`, `FILE_RECORD_HEADER`, `NTFS_ATTR_RECORD`, `NTFS_ATTRIBUTE_LIST_ITEM`.
- `STANDARD_INFORMATION`, `ATTRIBUTE_LIST`, `FILENAME_ATTRIBUTE`.
- Directory-index structures:
  - `INDEX_HEADER_ATTRIBUTE`
  - `INDEX_ROOT_ATTRIBUTE`
  - `INDEX_BUFFER`
  - `INDEX_ENTRY_ATTRIBUTE`
- B-tree helper structures:
  - `B_TREE_KEY`
  - `B_TREE_FILENAME_NODE`
  - `B_TREE`
- `VOLINFO_ATTRIBUTE`, `REPARSE_POINT_ATTRIBUTE`, and `FIXUP_ARRAY`.

## Inline Helper

`NtfsMarkIrpContextForQueue`

- Clears `IRPCONTEXT_COMPLETE`.
- Sets `IRPCONTEXT_QUEUE`.
- Returns `STATUS_PENDING`.

## Prototype Surface

The header exposes module contracts for:

- `attrib.c`: attribute creation, data-run conversion, attribute enumeration, filename/standard-info extraction, run packing, cluster freeing.
- `blockdev.c`: raw disk reads/writes, sector reads, device I/O controls.
- `btree.c`: directory index B-tree creation, insertion, split/demotion, serialization, and index-allocation updates.
- `cleanup.c`, `close.c`, `create.c`, `devctl.c`, `dirctl.c`, `dispatch.c`, `fastio.c`, `fcb.c`, `finfo.c`, `fsctl.c`.
- `mft.c`: attribute contexts, attribute I/O, file-record read/write, fixups, directory lookup, MFT growth, filename-index update.
- `misc.c`: IRP context and user-buffer helpers.
- `rw.c`: read/write dispatch handlers.
- `volinfo.c`: cluster allocation/free-space reporting and volume-information IRPs.
- `ntfs.c`: driver initialization and dispatch-table setup.

## Notable Details

- The header uses packed definitions for boot-sector structures, matching on-disk layout.
- Many structures intentionally mirror NTFS on-disk records, so field widths and alignment are critical.
- `MAX_PATH` is locally defined as 260 for FCB path buffers.
- Several comments mark speculative or incomplete knowledge, such as `FILE_RECORD_END` and resident indexed flags.
- Prototypes reveal unimplemented or limited areas elsewhere: write support, directory B-tree mutation, sparse/compressed/encrypted handling, large-file limits, and volume mutation.
