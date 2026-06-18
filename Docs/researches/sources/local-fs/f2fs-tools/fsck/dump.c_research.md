# File Research: sources/local-fs/f2fs-tools/fsck/dump.c

## Purpose
Implements `dump.f2fs` metadata dumps, file recovery/extraction, inode traversal, xattr restoration, and block-address diagnostics.

## Key functionality
- Metadata dump files:
  - `nat_dump` writes `dump_nat`.
  - `sit_dump` writes `dump_sit`.
  - `ssa_dump` writes `dump_ssa`.
- File/directory extraction:
  - `dump_node` validates NAT/SIT and node footer, prints node info, and dumps inode contents.
  - `dump_inode_blk` traverses inline data, inline dentries, direct addresses, direct nodes, indirect nodes, and double-indirect nodes.
  - `dump_data_blk` reads data blocks or recursively dumps directory contents.
  - `dump_file`, `dump_link`, and `dump_folder` create recovered filesystem objects.
  - `dump_filesystem` handles user prompting, base path creation, encrypted/nodump rejection, permission preservation, and recursive directory dumping.
- Xattr restore:
  - `dump_xattr` reads all xattrs, validates bounds, maps F2FS xattr indexes to platform prefixes, and sets xattrs on output files/directories/symlinks when supported.
- Diagnostics:
  - `dump_info_from_blkaddr` classifies an arbitrary block as reserved/metadata/SIT/NAT/SSA/user data, reads SSA summary, maps to NAT/node/inode, and optionally dumps dentry contents.
  - `dump_node_scan_disk` brute-force scans main-area node segments for a given inode/nid.
  - `start_bidx_of_node`, `dump_data_offset`, and `dump_node_offset` compute logical offsets from node offsets.

## Dependencies
Uses:
- `node.h`, `fsck.h`, `xattr.h`
- platform xattr headers when available
- global `c` dump options and file descriptors
- block IO helpers such as `dev_read_block`, `dev_write_dump`, `dev_write_symlink`
- F2FS metadata helpers: `get_node_info`, `get_sum_entry`, `get_sum_block`, `is_sit_bitmap_set`, `make_dentry_ptr`

## Important behavior
- Hard links are not reconstructed as hard links during dump; the code warns they may be duplicated.
- Encrypted files are refused because names/data cannot be safely interpreted.
- File map mode prints extents instead of writing file contents.
- Inline symlinks and inline regular data are handled before normal block traversal.

## Research notes
This file is read-mostly recovery tooling, but it still writes host filesystem output and may set ownership/mode/xattrs. Its F2FS-side writes are not part of normal dumping, aside from shared helper behavior elsewhere.
