# File Research: sources/local-fs/f2fs-tools/fsck/dqblk_v2.h

## Purpose
Header for version-2 quota file format state.

## Key structures
- `struct v2_mem_dqinfo`:
  - embeds quota tree metadata `qtree_mem_dqinfo`
  - stores quota file flags
  - tracks used entries and data blocks, updated during dquot scanning
- `struct v2_mem_dqblk`:
  - stores offset of a dquot record in the quota file

## Key declarations
- Forward-declares `struct quotafile_ops`.
- Externs `quotafile_ops_2`, the operation table for this quota format.

## Dependencies
Includes `quotaio_tree.h`.

## Research notes
This file is quota-format plumbing. It does not implement quota logic itself; it declares format-specific in-memory structures used by quota IO code.
