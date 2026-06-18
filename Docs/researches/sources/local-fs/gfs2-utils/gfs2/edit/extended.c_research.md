# File Research: sources/local-fs/gfs2-utils/gfs2/edit/extended.c

## Purpose
Implements the extended display mode for `gfs2_edit`, showing indirect pointers, directory entries, resource group indexes, journal status, and system-file contents beyond raw hex/structure views.

## Main Elements
- Indirect scanning: `_do_indirect_extended()` and `do_indirect_extended()` parse nonzero 64-bit block pointers and preserve metapath indexes.
- Inode context helpers: `get_height()`, `dinode_valid()`, and `metapath_to_lblock()` infer height and file offsets from navigation history.
- Display routines:
  - `display_indirect()` prints indirect block lists and optional recursive details.
  - `display_leaf()` prints directory leaf metadata and dirents.
  - `print_block_details()` recursively reads indirect/leaf chains in non-curses output.
- System-file views:
  - `print_gfs2_jindex()` lists journals and clean/dirty status.
  - `parse_rindex()` prints rindex or backing rgrp data.
  - `print_inum()`, `print_statfs()`, `print_quota()` decode system inode contents.
- `display_extended()` dispatches based on current block identity and available metadata.

## Dependencies And Integration
Uses global editor state from `hexedit.h`, libgfs2 inode/buffer helpers, `gfs2hex.c` directory decoding, and `struct_print.c` field printers. Called from `display()` when `dmode == EXTENDED_MODE`.

## Risk Notes
Several paths read blocks directly from `sbd.device_fd` and may exit on short reads. Recursive display trusts pointer structures enough to follow them for reporting, so corrupt filesystems can produce noisy or aborting diagnostics.
