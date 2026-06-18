# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/generic.c

This file provides the broad ext2/ext3/ext4 metadata support layer used by the Windows driver. It loads/saves superblocks, group descriptors, inodes, and buffers; manages block and inode allocation bitmaps; updates directory entries and link counts; initializes uninitialized ext4 bitmaps; computes group-descriptor checksums; and exposes ext3/ext4 helper accessors.

Key responsibilities:
- Load, refresh, save, and flush volume metadata.
- Manage buffer-head caches for group descriptors and metadata blocks.
- Translate raw ext3 inodes to/from in-memory `struct inode`.
- Allocate and free blocks and inodes while maintaining bitmaps, group descriptors, and superblock counts.
- Add/remove directory entries and update directory parent/file type metadata.
- Validate directory entries and compute maximum file sizes.
- Support ext4-style 64-bit descriptor fields, huge-file block counts, metadata checksums, sparse-super/meta-bg layouts, and uninitialized bitmaps.

Important functions:
- `Ext2LoadSuper`, `Ext2SaveSuper`, `Ext2RefreshSuper`: Superblock I/O and root inode refresh.
- `Ext2LoadGroup`, `Ext2LoadGroupBH`, `Ext2DropGroupBH`, `Ext2PutGroup`: Group-descriptor block discovery, loading, validation, and release.
- `Ext2DropBH`, `Ext2FlushRange`, `Ext2FlushVcb`: Metadata buffer cleanup and volume cache flushing while skipping live buffer-head ranges.
- `Ext2GetInodeLba`, `Ext2LoadInode`, `Ext2SaveInode`, `Ext2ClearInode`: Inode table addressing and raw inode persistence.
- `Ext2DecodeInode`, `Ext2EncodeInode`: Convert mode, flags, uid/gid, size, acl, times, blocks, extents/block map, and extra inode size.
- `Ext2LoadInodeXattr`, `Ext2SaveInodeXattr`: Read/save the inode tail area used for inline xattr storage.
- `Ext2LoadBlock`, `Ext2SaveBlock`, `Ext2LoadBuffer`, `Ext2ZeroBuffer`, `Ext2SaveBuffer`: Block/range I/O through buffer heads or ReactOS cache pinning.
- `Ext2NewBlock`, `Ext2FreeBlock`: Allocate/free contiguous block runs using group bitmaps and update free-block counts.
- `Ext2NewInode`, `Ext2FreeInode`, `Ext2UpdateGroupDirStat`: Allocate/free inode bitmap bits, choose target groups, update directory counts, and initialize lazy bitmaps.
- `Ext2AddEntry`, `Ext2RemoveEntry`, `Ext2SetFileType`, `Ext2SetParentEntry`: Higher-level directory mutations around ext3 directory helpers.
- `ext3_check_dir_entry`, `ext3_next_entry`: Directory record validation and traversal.
- `ext3_inode_blocks`, `ext3_inode_blocks_set`: Decode/encode 32-bit, 48-bit, and huge-file `i_blocks`.
- `ext4_*_count`, `ext4_*_set`, `ext4_get_group_desc`: Accessors for 64-bit-capable group descriptor fields.
- `crc16`, `ext4_group_desc_csum`, `ext4_group_desc_csum_verify`: Group descriptor checksum support.
- `ext3_bg_has_super`, `ext4_bg_num_gdb`, `descriptor_loc`: Sparse-super, meta block group, and descriptor-location helpers.
- `ext4_init_inode_bitmap`, `ext4_init_block_bitmap`, `ext4_check_descriptors`: Lazy bitmap initialization and descriptor validation.

Important interactions:
- Uses Linux-derived ext3/ext4 structures but maps storage through Ext2Fsd `VCB`, cache manager, and buffer-head wrappers.
- Directory mutations call htree/dirent helpers such as `ext3_add_entry`, `ext3_find_entry`, `ext3_delete_entry`, `ext3_set_de_type`, and `ext3_mark_inode_dirty`.
- Allocation paths serialize on `Vcb->MetaBlock` and `Vcb->MetaInode`.
- Superblock and group descriptor statistics are recalculated through `ext4_count_free_blocks` and `ext4_count_free_inodes`.

Notable behavior and risks:
- Allocation code sometimes repairs stale free-count metadata by setting a group's free count to zero and retrying another group.
- Newly allocated blocks are removed from dirty MCB extents to avoid volume lazy writing of metadata ranges.
- `Ext2SaveInode` reads the existing raw inode before encoding, preserving fields not represented in the in-memory inode.
- `Ext2LoadInodeXattr` reads the raw inode and then calls `Ext2EncodeInode` into the same buffer, so callers get current in-memory inode core fields plus raw tail data.
- `Ext2FlushVcb` asserts exclusive `MainResource`, then takes descriptor and buffer-head locks while flushing cache ranges outside live buffer heads.
