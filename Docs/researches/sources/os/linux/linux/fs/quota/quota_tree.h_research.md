# File Research: sources/os/linux/linux/fs/quota/quota_tree.h

Header for quota-tree block layout.

Defines:
- `struct qt_disk_dqdbheader`, the 16-byte header at the start of quota data blocks.
  - `dqdh_next_free`: next block in free-entry list.
  - `dqdh_prev_free`: previous block in free-entry list.
  - `dqdh_entries`: number of valid entries in the block.
  - padding fields to keep the header at 16 bytes.
- `QT_TREEOFF`, the block offset of the quota tree root.

Research notes:
- The 16-byte header size is chosen so a standard v2 data block has predictable room for quota entries.
- Used by `quota_tree.c` and v2 quota format support.
