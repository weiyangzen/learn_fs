# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4.h

This header provides selected ext4 compatibility definitions and includes the ext4 journal and extent headers.

Major content:
- Includes JBD and ext3 format headers.
- Defines Windows-style fixed-width typedefs `uint16_t`, `uint32_t`, `uint64_t`, then ext4 logical and filesystem block typedefs.
- Defines `EXT4_GET_BLOCKS_*` flags for allocation, unwritten extent conversion, delayed allocation, direct I/O, metadata no-fail, fallocate, lock/cache behavior, and unwritten conversion.
- Defines extent lookup/cache flags `EXT4_EX_NOCACHE` and `EXT4_EX_FORCE_CACHE`.
- Defines `EXT4_FREE_BLOCKS_*` flags.
- Defines multiblock allocator hint flags.
- Aliases `ext4_sb_info` to `ext3_sb_info`, provides `EXT4_SB`, and defines `EXT4_I(i)` as identity.

Role:
- Adapts ext4 extent code to the ext3-based in-memory structures used by this driver.
- Does not define a full Linux ext4 VFS layer; it exposes only the pieces needed by Ext2Fsd extent and allocation code.
