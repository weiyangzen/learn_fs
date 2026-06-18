# File Research: sources/local-fs/gfs2-utils/gfs2/edit/struct_print.h

## Purpose
Declares structured print functions for GFS2 on-disk metadata.

## Main Elements
- Prototypes for superblock, dinode, log, quota, statfs, eattr, leaf, rindex, and rgrp printers.
- Comments note that functions expect on-disk data.

## Dependencies And Integration
Included by editor display modules that decode metadata buffers.

## Risk Notes
No type-specific parameters in prototypes, only `void *`, so callers must pass the correct on-disk structure.
