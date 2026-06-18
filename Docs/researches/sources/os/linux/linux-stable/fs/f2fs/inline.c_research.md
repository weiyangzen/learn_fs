# File Research: sources/os/linux/linux-stable/fs/f2fs/inline.c

`inline.c` implements inline data and inline dentry support, where small regular files, symlinks, or directories store payload inside the inode node page instead of separate data blocks.

Inline-data eligibility rejects atomic-write files, non-regular/non-symlink files, oversized files, and post-read-required files such as encrypted/verity/compressed data. Sanity checks detect impossible inline states, such as inline-data inodes that also have block pointers or unsupported feature combinations.

The read/write helpers copy inline payload between the inode node page and page-cache folio zero. `f2fs_do_read_inline_data()` copies inode-resident bytes and zeroes the rest of the folio; `f2fs_write_inline_data()` copies dirty page-cache data back into the inode page, marks append/data-exist state, and clears the page-cache dirty tag. `f2fs_truncate_inline_inode()` zeroes inline bytes from a truncation offset and clears `FI_DATA_EXIST` when truncating to zero.

Inline-to-block conversion is handled by `f2fs_convert_inline_inode()` and `f2fs_convert_inline_folio()`. They reserve block zero, verify the reserved address is `NEW_ADDR`, copy inline data into a page-cache folio, submit an out-of-place write, wait for completion, mark the inode recoverable through `FI_APPEND_WRITE`, clear inline bytes and inline flags, and update inline inode stats. Corrupt inline block state sets fsck-needed state and reports an invalid block address.

Recovery support reconciles roll-forward inode pages with current inline state. `f2fs_recover_inline_data()` handles all combinations of previous and recovered inline flags: copy inline data, remove inline data and recover blocks, truncate blocks and restore inline data, or leave block recovery to the normal path.

Inline directory support includes lookup, empty-dir initialization, insertion, deletion, readdir, empty-dir checks, and conversion to normal dentry blocks. If an inline directory overflows, level-zero directories copy the inline dentry structure into block zero; hashed/rehashed directories back up inline dentries, clear inline storage, and reinsert entries through regular directory insertion so hashes and placement are rebuilt. Failure paths restore inline contents or truncate partially created dentry pages.

`f2fs_inline_data_fiemap()` reports inline regular/symlink data or inline dentries as FIEMAP inline extents, optionally syncing the inode node first and calculating the byte address inside the inode block when the inode node has a valid physical address.

Important dependencies are inode node pages, dnode/block reservation, data writeback, directory entry helpers, filename setup, fiemap, node info, inline xattr sizing, and F2FS recovery flags. The main invariants are that inline inodes cannot simultaneously own separate data blocks, conversion must not expose uninitialized dentry memory, and inline flag/stat changes must be synchronized with inode-page dirtiness and recovery expectations.
