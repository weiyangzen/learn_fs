# File Research: sources/windows/reactos/drivers/filesystems/fastfat/nodetype.h

This header defines FastFAT node type codes, bugcheck identifiers, ASCII control constants, and pool allocation tags.

Key responsibilities:
- Assign stable `NODE_TYPE_CODE` values to core in-memory records:
  - data header
  - VCB
  - FCB
  - DCB
  - root DCB
  - CCB
  - IRP context
- Provide the `NodeType(Ptr)` macro used throughout the driver to validate object identity.
- Define per-source-file bugcheck IDs used by `FatBugCheck`.
- Define `FatBugCheck(A,B,C)` as a wrapper around `KeBugCheckEx(FAT_FILE_SYSTEM, ...)`.
- Provide `UCHAR_*` constants for ASCII/control characters used in FAT name handling.
- Define pool tags for FastFAT allocations: FCBs, CCBs, ERESOURCEs, IRP contexts, BCBs, dirents, bitmaps, EA data, close contexts, I/O contexts, VPBs, dynamic name buffers, and related buffers.

Important constants:
- `FAT_NTC_VCB`, `FAT_NTC_FCB`, `FAT_NTC_DCB`, `FAT_NTC_ROOT_DCB`, `FAT_NTC_CCB`, `FAT_NTC_IRP_CONTEXT`.
- `FAT_BUG_CHECK_NAMESUP`, `FAT_BUG_CHECK_PNP`, `FAT_BUG_CHECK_READ`, `FAT_BUG_CHECK_RESRCSUP`, `FAT_BUG_CHECK_SHUTDOWN`, `FAT_BUG_CHECK_SPLAYSUP`, `FAT_BUG_CHECK_STRUCSUP`, `FAT_BUG_CHECK_TIMESUP`.
- Allocation tags such as `TAG_FCB`, `TAG_CCB`, `TAG_FCB_NONPAGED`, `TAG_ERESOURCE`, `TAG_IRP_CONTEXT`, `TAG_FILENAME_BUFFER`, `TAG_FAT_IO_CONTEXT`, and `TAG_DYNAMIC_NAME_BUFFER`.

Notable behavior and risks:
- The node-type convention assumes the first field of major structures is a `NODE_TYPE_CODE`.
- The bugcheck macro combines each file’s `BugCheckFileId` with `__LINE__`, making source line numbers part of crash diagnostics.
