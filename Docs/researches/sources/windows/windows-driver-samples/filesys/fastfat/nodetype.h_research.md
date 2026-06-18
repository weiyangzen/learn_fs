# File Research: sources/windows/windows-driver-samples/filesys/fastfat/nodetype.h

## Purpose
Defines common FAT node type codes, bugcheck file IDs, ASCII control constants, and pool allocation tags. This header provides shared identity and diagnostics metadata for the FastFAT implementation.

## Main Definitions
- `NODE_TYPE_CODE`: `USHORT` type used as the first field of major FAT structures.
- `NODE_BYTE_SIZE`: byte-size type paired with `NODE_TYPE_CODE`.
- `NodeType(Ptr)`: macro that reads the leading node type code from a structure.
- FAT node codes:
  - `FAT_NTC_DATA_HEADER`
  - `FAT_NTC_VCB`
  - `FAT_NTC_FCB`
  - `FAT_NTC_DCB`
  - `FAT_NTC_ROOT_DCB`
  - `FAT_NTC_CCB`
  - `FAT_NTC_IRP_CONTEXT`

## Bugcheck Support
Defines per-source-file bugcheck ID high words such as:
- `FAT_BUG_CHECK_LOCKCTRL`
- `FAT_BUG_CHECK_NAMESUP`
- `FAT_BUG_CHECK_PNP`
- `FAT_BUG_CHECK_READ`
- `FAT_BUG_CHECK_RESRCSUP`
- `FAT_BUG_CHECK_SHUTDOWN`
- `FAT_BUG_CHECK_SPLAYSUP`

`FatBugCheck(A,B,C)` calls `KeBugCheckEx` with `FAT_FILE_SYSTEM` and combines the file-specific `BugCheckFileId` with `__LINE__`, giving crash diagnostics both file and line identity.

## Constants And Tags
The file defines byte constants for ASCII control characters from `UCHAR_NUL` through `UCHAR_SP`.

When not building the filesystem debugger extension, it defines pool tags for key allocations:
- Control structures: `TAG_CCB`, `TAG_FCB`, `TAG_FCB_NONPAGED`, `TAG_IRP_CONTEXT`
- Cache and metadata buffers: `TAG_BCB`, `TAG_DIRENT`, `TAG_FAT_BITMAP`, `TAG_FILENAME_BUFFER`
- I/O contexts and buffers: `TAG_FAT_IO_CONTEXT`, `TAG_IO_RUNS`, `TAG_IO_BUFFER`, `TAG_IO_USER_BUFFER`
- Verification and defrag helpers: `TAG_VERIFY_BOOTSECTOR`, `TAG_VERIFY_ROOTDIR`, `TAG_DEFRAG_BUFFER`

## Important Notes
Most FastFAT structures rely on the convention documented here: the first fields are node type and node byte size. Many files use `NodeType` for defensive runtime validation before casting generic filesystem pointers to VCB/FCB/DCB/CCB structures.
