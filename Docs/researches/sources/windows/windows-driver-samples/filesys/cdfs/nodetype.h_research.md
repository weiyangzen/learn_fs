# File Research: sources/windows/windows-driver-samples/filesys/cdfs/nodetype.h

## Purpose

Defines CDFS node type codes, node-size conventions, node-type access macros, and per-source bugcheck IDs.

## Key Definitions

The file declares `NODE_TYPE_CODE`, `PNODE_TYPE_CODE`, and `NODE_BYTE_SIZE`. It assigns stable codes for core CDFS runtime objects:

- `CDFS_NTC_DATA_HEADER`
- `CDFS_NTC_VCB`
- `CDFS_NTC_FCB_PATH_TABLE`
- `CDFS_NTC_FCB_INDEX`
- `CDFS_NTC_FCB_DATA`
- `CDFS_NTC_FCB_NONPAGED`
- `CDFS_NTC_CCB`
- `CDFS_NTC_IRP_CONTEXT`
- `CDFS_NTC_IRP_CONTEXT_LITE`

`NodeType(P)` safely returns `NTC_UNDEFINED` for null pointers. `SafeNodeType(Ptr)` directly reads the first node-type field.

The bugcheck constants give each CDFS source file a high-word identifier. `CdBugCheck(A,B,C)` calls `KeBugCheckEx(CDFS_FILE_SYSTEM, BugCheckFileId | __LINE__, A, B, C)` so crashes encode both module and source line.

## Integration

All major CDFS structures are expected to begin with `NodeTypeCode` and `NodeByteSize`. Runtime code uses these codes to distinguish VCBs, FCB variants, CCBs, and IRP contexts during decode, teardown, PnP, and assertions.
