# File Research: sources/os/linux/linux/fs/ext4/resize.c

## Purpose
Implements online ext4 filesystem growth: adding blocks to the current group, adding new block groups/flex groups, publishing new group descriptors, updating superblock counters, maintaining backup metadata, and converting from `resize_inode` to `meta_bg` when reserved GDT capacity is exhausted.

## Main Entry Points
- `ext4_resize_begin()` / `ext4_resize_end()` gate online resize with capability, mount-state, feature, and single-resizer checks.
- `ext4_group_extend()` extends the current final group.
- `ext4_group_add()` adds one externally described group.
- `ext4_resize_fs()` orchestrates full growth to a requested block count.
- `ext4_list_backups()` enumerates groups containing backup superblocks/GDTs.

## Metadata Planning
`verify_group_input()` validates externally supplied group metadata placement. For 64-bit/flex resizing, `alloc_flex_gd()` allocates bounded flex-group planning arrays, `ext4_setup_next_flex_gd()` fills group descriptors for the next growth batch, and `ext4_alloc_group_tables()` chooses block bitmap, inode bitmap, and inode table locations across flex groups while accounting metadata blocks and uninitialized flags.

## New Group Initialization
`setup_new_flex_group_blocks()` runs a preparatory journaled phase outside the main publication transaction. It copies backup GDT blocks, zeroes reserved GDT blocks, zeroes inode tables when needed, initializes block and inode bitmaps, marks metadata clusters used, and handles uninitialized bitmap/table flags. `bclean()` obtains and zeroes journaled metadata buffers.

## Descriptor Publication
`ext4_flex_group_add()` is the main publish transaction. It gets superblock write access, calls `ext4_add_new_descs()` to add or expose group descriptor blocks, initializes new descriptors with `ext4_setup_new_descs()`, and then calls `ext4_update_super()` to make new blocks/groups/inodes visible. `ext4_update_super()` updates global counts, group count, blockfile group limit, reserved blocks, percpu counters, flex-group counters, overhead accounting, and the superblock checksum with memory barriers around `s_groups_count`.

## GDT and Backup Handling
`add_new_gdb()` consumes reserved GDT blocks from the resize inode and publishes a new primary group descriptor block via RCU pointer replacement. `add_new_gdb_meta_bg()` adds a descriptor block for meta_bg mode. `reserve_backup_gdb()` adds future reserved backup GDT references into the resize inode. `update_backups()` refreshes backup superblocks/GDTs after successful resize and marks the filesystem for fsck if backup update fails.

## Full Resize Orchestration
`ext4_resize_fs()` verifies the target device size, cluster-aligns bigalloc sizes, rejects shrinking, checks inode-count overflow, handles reserved GDT limits, opens the resize inode as needed, converts to `meta_bg` when necessary, extends a partial last group, allocates flex and multiblock allocator metadata arrays, and repeatedly adds flex groups until the requested size is reached or an error occurs. It retries after conversion or after exhausting reserved descriptor capacity.

## Integration Points
Depends on ext4 superblock/group descriptor layout, flex_bg, sparse_super/sparse_super2, meta_bg, resize_inode, bigalloc, metadata checksums, JBD2 journaling, multiblock allocator group info, RCU-protected descriptor/flex arrays, buffer-head metadata I/O, and backup-superblock rules.

## Invariants and Risks
Resize front-loads validation because journaled metadata updates cannot be rolled back once publication begins. The ordering in `ext4_update_super()` is critical: block/inode counts and descriptors must be valid before `s_groups_count` exposes new groups. Backup update failure is non-fatal but forces fsck. Feature combinations such as sparse_super2 online resize, simultaneous resize_inode/meta_bg, and resizing from backup superblocks are rejected.

## Testing Signals
Cover extending only the last group, adding groups with and without flex_bg, metadata checksums, sparse backups, reserved GDT exhaustion, conversion to meta_bg, bigalloc target trimming, failure to read target last block, backup update failure, RCU descriptor replacement, and allocator group-info allocation failure.
