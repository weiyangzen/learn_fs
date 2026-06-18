# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_attr_inactive.c

## Purpose

Removes an inode’s entire attribute fork during inode inactivation, including remote attribute value buffers, attr tree blocks, extents, and the incore attr fork.

## Main Responsibilities

- Invalidates incore buffers for remote attr value extents.
- Walks attr leaf blocks and stales remote values referenced by entries.
- Recursively walks attr node trees depth-first.
- Removes child references from parent nodes as blocks are invalidated.
- Reinitializes root blocks before truncation so crash recovery sees safe empty metadata.
- Truncates attr fork extents and removes the attr fork.
- Zaps the incore attr fork even when errors occur.

## Data Flow

`xfs_attr_inactive` allocates an attr invalidation transaction, locks and joins the inode, invalidates attr tree contents with `xfs_attr3_root_inactive`, truncates all attr fork extents, calls `xfs_attr_fork_remove`, and commits.

## Important Invariants

- Remote attr value buffers are never logged, so stale marking is safe before `bunmapi`.
- Tree traversal is bounded by `XFS_DA_NODE_MAXDEPTH`; exceeding it marks the attr fork sick and returns corruption.
- Attribute fork removal must handle inodes that have an attr fork but no attributes.
- The in-memory attr fork is removed even on error before dropping the inode lock.

## Dependencies

- Attr leaf/node helpers.
- Remote attr helpers.
- Bmap truncation.
- Transaction rolling and buffer invalidation.
- XFS health reporting for sick attr forks.

## Research Notes

The crash-safety detail is important: leaves are emptied before extents are truncated so a mid-operation crash cannot leave leaf entries pointing at freed remote value blocks.
