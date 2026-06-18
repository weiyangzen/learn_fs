# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/fsck.h

## Purpose
Central shared header for `fsck.gfs2`, defining exit codes, core bookkeeping structures, global pass state, validation helpers, and pass/function declarations.

## Main Elements
- Constants: fsck-compatible exit codes, hash sizes, max format, bad pointer tolerance.
- Core structs:
  - `bmap` for bitmap storage.
  - `inode_info`, `dir_info`, `dir_status` for inode/directory accounting.
  - `duptree`, `inode_with_dups`, and `enum dup_ref_type` for duplicate block tracking.
  - `enum rgindex_trust_level` for resource group index confidence.
  - `fsck_options` and `fsck_cx` for runtime options and context.
  - `special_blocks` list node.
- Function declarations for initialization/destruction, passes 1-5, rindex repair, query, inode helpers, duplicate/directory tree operations, and filesystem skeleton rebuild helpers.
- Global externs for lost+found, pass control, error counters, duplicate counters, and filesystem block bounds.
- Inline validation helpers: `valid_block()`, `rgrp_contains_block()`, and `valid_block_ip()`.

## Dependencies And Integration
Included across fsck modules. Depends on libgfs2 and `osi_tree.h` data structures.

## Risk Notes
Many globals coordinate pass behavior, so ordering and reset semantics matter. `valid_block()` and `valid_block_ip()` are core safety gates before repair operations.
