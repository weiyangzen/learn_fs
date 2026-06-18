# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs_i.h

This header defines ext3/ext4 block-number typedefs and the in-memory ext3 inode sidecar structure.

Key definitions:
- Block group and filesystem block typedefs: `ext3_grpblk_t`, `ext4_grpblk_t`, `ext3_fsblk_t`, `ext4_fsblk_t`, `ext3_lblk_t`, `ext4_lblk_t`, `ext3_group_t`, `ext4_group_t`.
- Reservation window structures: `ext3_reserve_window`, `ext3_reserve_window_node`.
- Block allocation tracking: `ext3_block_alloc_info`.

`struct ext3_inode_info` contains:
- Raw block pointer array, inode flags, ACL/dir/dtime fields, block group, dynamic state, reservation info, directory lookup hint, optional xattr/ACL fields, orphan-list entry, on-disk size tracking, extra inode size, and embedded `struct inode`.

Role:
- Supplies Linux ext3 allocator and inode state expected by borrowed ext3 code.
- In this ReactOS port, `EXT3_I(inode)` returns the inode directly, so only fields mirrored in the local `struct inode` are usable unless the sidecar is explicitly embedded elsewhere.

Notable detail:
- Comments preserve Linux truncate/recovery reasoning around `i_disksize`, but the truncate mutex block is disabled.
