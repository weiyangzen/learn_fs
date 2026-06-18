# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/dir.c

## Purpose

Validates and repairs FAT directory trees, long filename records, file sizes, dot entries, directory connectivity, and lost-chain reconnection into `LOST.DIR`.

## Main Entry Points

- `resetDosDirSection(struct fat_descriptor *fat)`: allocates buffers and initializes root directory state.
- `finishDosDirSection(void)`: frees pending directory nodes, directory tree nodes, and buffers.
- `handleDirTree(struct fat_descriptor *fat)`: scans root and pending subdirectories.
- `reconnect(struct fat_descriptor *fat, cl_t head, size_t length)`: creates entries in `LOST.DIR` for lost chains.
- `finishlf(void)`: frees lost-file working buffer.

## Directory Model

Uses `struct dosDirEntry` nodes linked by parent/child/next to represent the discovered tree, and `struct dirTodoNode` as a pending stack for breadth/depth traversal.

## Important Logic

- Long filename handling:
  - Tracks LFN sequence records in `longName`.
  - Verifies sequence index, checksum against short 8.3 name, zero cluster field, and maximum length.
  - `removede()` deletes invalid LFN runs when approved.
- Directory slot handling:
  - Detects entries after `SLOT_EMPTY`.
  - Offers to extend by deleting empty-slot gap or truncate/delete later entries.
- Cluster validation:
  - Ensures non-empty files and directories start at valid unclaimed FAT chain heads.
  - Invalid directories can be deleted; invalid files can be truncated to size zero.
- File size validation:
  - `checksize()` compares directory size with checked chain size.
  - Can truncate size or drop superfluous FAT clusters.
- Subdirectory validation:
  - `check_subdirectory()` verifies first entries are `.` and `..` with directory attributes.
  - During main scan, repairs incorrect `.` and `..` starting cluster fields.
- Lost chain reconnection:
  - `reconnect()` finds free slots in `LOST.DIR`, writes an 8.3 numeric name based on head cluster, and records the chain as a file.

## Integration Points

Uses `fat_get_cl_next()`, `fat_set_cl_next()`, `fat_is_valid_cl()`, `fat_is_cl_head()`, `checkchain()`, and `clearchain()` from `fat.c`. Uses BPB/layout values from `struct bootblock`.

## Risk Notes

Directory writes happen cluster-by-cluster, while FAT changes are delayed elsewhere. LFN deletion across cluster boundaries is particularly delicate and handled through `delete()` plus in-buffer slot updates.
