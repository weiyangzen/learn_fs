# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_set_slot_count.c

## Role

Implements `-N/--node-slots <count>`, increasing or decreasing the maximum number of OCFS2 node slots. This is one of the most invasive tunefs operations because slots own journals, local allocators, orphan dirs, truncate logs, and quota files.

## Parse Flow

`set_slot_count_parse_option()` parses a positive integer with `strtol()`, rejects non-numeric input, overflow sentinel values, values below 1, and values above `INT_MAX`. It defers filesystem-format-specific max validation until the filesystem is open.

## Increasing Slots

`add_slots()` determines the max slot count from slot map format:

- extended slot map: `INT16_MAX`
- old slot map: `OCFS2_MAX_SLOTS`

It creates per-slot system files for each new slot and each non-global system inode type. It skips local quota files unless the corresponding quota feature is enabled. Directory system inodes are initialized with `ocfs2_init_dir()`, all new inodes are linked into the system directory, and local quota files are initialized when created.

After adding slots, `update_slot_count()` sets `s_max_slots`, calls `tunefs_set_journal_size(fs, 0, ...)` to allocate space for new journals, formats the slot map, and writes the superblock.

## Decreasing Slots

Before removing slots, `remove_slot_check()` ensures slots being removed are safe:

- orphan directories must be empty
- local alloc files must be empty
- truncate logs must be empty

`remove_slots()` sets `OCFS2_TUNEFS_INPROG_REMOVE_SLOT`, then removes slots one at a time from the highest slot downward. For each removed slot it:

1. Relinks extent allocator chains into remaining slots.
2. Relinks inode allocator chains into remaining slots.
3. Truncates the removed slot's orphan directory.
4. Zeroes and truncates the removed slot's journal.
5. Truncates local quota files when quota is enabled.
6. Decrements `s_max_slots` and writes the primary superblock before deleting system dir entries.
7. Deletes system directory entries for the removed slot.
8. Decrements the system directory link count for the removed orphan dir.

`update_slot_count()` clears the remove-slot in-progress flag only after successful removal, formats the slot map, and writes the final superblock.

## Allocator Relinking

`relink_system_alloc()` moves allocator chain records from a removed slot to remaining slots.

`move_chain_rec()` reads all group descriptors in a chain into a temporary reversed list, updates suballocator slot metadata in allocated inodes or extent blocks, and moves each group to a destination allocator.

`move_group()` rewrites group descriptor parent/chain linkage and updates destination bitmap inode totals, free counts, cluster counts, and size.

This careful order is designed so `fsck.ocfs2` can recover or continue after failures.

## Journal Cleanup

`empty_journal()` writes zeroes over the journal contents before truncation. The comment explains this prevents old journal blocks from later looking like valid inode blocks if the space is reused.

## Metadata Touched

- System directory entries
- Per-slot system inodes
- Local quota files
- Orphan dirs
- Journals
- Extent and inode allocator chain records
- Group descriptors
- Inode/extent suballocator slot fields
- Superblock `s_max_slots`
- Slot map
- Tunefs in-progress flags

## Open Flags

Declared as `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`.

## Notable Risks

- Very high blast radius. Failures can leave partially moved allocator groups or removed-slot artifacts, although the operation uses in-progress state and ordering to aid fsck recovery.
- `decrease_link_count()` takes `uint16_t blkno`, but inode block numbers elsewhere are `uint64_t`. Passing `fs->fs_sysdir_blkno` through `uint16_t` can truncate block numbers on large filesystems.
- `remove_slot_iterate()` computes `dname + (dirent->name_len - taillen)` without first checking that `dirent->name_len >= taillen`; malformed or unexpected short names can underflow the pointer.
