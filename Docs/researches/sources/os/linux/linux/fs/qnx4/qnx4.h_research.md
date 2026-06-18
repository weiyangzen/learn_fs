# File Research: sources/os/linux/linux/fs/qnx4/qnx4.h

## Role

Private QNX4 driver header.

## Key Definitions

- `struct qnx4_sb_info`: stores version and copied bitmap inode entry.
- `struct qnx4_inode_info`: stores raw QNX4 inode entry, `mmu_private`, and embedded VFS inode.
- Helper accessors:
  - `qnx4_sb()`
  - `qnx4_i()`
  - `qnx4_raw_inode()`
- `union qnx4_directory_entry`: overlays inode entries, link entries, and a generic name/status view.

## Directory Entry Helper

- `get_entry_fname()` validates non-empty names and used/link status bits, selects the correct fixed name length for inode vs link entries, applies `strnlen()`, and returns the common name pointer.
- Includes `BUILD_BUG_ON()` checks that status byte offsets match across entry formats.

## Research Notes

The union intentionally uses a synthetic `de_name[48]` to avoid GCC false-positive array-bounds behavior when accessing overlaid QNX4 inode/link name arrays.
