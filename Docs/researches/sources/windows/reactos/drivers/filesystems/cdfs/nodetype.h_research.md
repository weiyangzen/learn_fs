# File Research: sources/windows/reactos/drivers/filesystems/cdfs/nodetype.h

## Purpose

`nodetype.h` defines CDFS node type codes and bugcheck file IDs. It establishes the convention that major CDFS structures begin with a `NODE_TYPE_CODE` followed by a `NODE_BYTE_SIZE`.

## Node Type Definitions

The header defines:

- `NODE_TYPE_CODE` as `USHORT`
- `NODE_BYTE_SIZE` as `CSHORT`
- `NTC_UNDEFINED`
- CDFS node codes for:
  - data header
  - VCB
  - path-table FCB
  - index FCB
  - data FCB
  - nonpaged FCB
  - CCB
  - IRP context
  - lite IRP context

It also defines:

- `NodeType(P)`: returns the first node type code or `NTC_UNDEFINED` for null.
- `SafeNodeType(Ptr)`: directly reads the node type code.

## Bugcheck IDs

The header assigns file-specific high-word IDs such as:

- `CDFS_BUG_CHECK_DIRSUP`
- `CDFS_BUG_CHECK_FILEINFO`
- `CDFS_BUG_CHECK_FILOBSUP`
- `CDFS_BUG_CHECK_FSCTRL`
- `CDFS_BUG_CHECK_FSPDISP`
- `CDFS_BUG_CHECK_LOCKCTRL`
- `CDFS_BUG_CHECK_NAMESUP`

and many other CDFS modules.

`CdBugCheck(A,B,C)` calls `KeBugCheckEx(CDFS_FILE_SYSTEM, BugCheckFileId | __LINE__, A, B, C)`, combining the module’s `BugCheckFileId` with the source line.

## Dependencies

The header assumes kernel types such as `USHORT`, `CSHORT`, and `KeBugCheckEx` are available from included Windows/ReactOS headers.

## Research Notes

This header is a diagnostic and structural identity foundation. Runtime validation and debugging can quickly identify CDFS object kinds through the first two fields, while bugchecks include both module identity and line number.
