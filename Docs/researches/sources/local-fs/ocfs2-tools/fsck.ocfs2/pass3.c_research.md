# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass3.c

Purpose: implements fsck pass 3, ensuring directory tree connectivity, recreating root or `/lost+found` when needed, reconnecting disconnected directories/files, and fixing inconsistent `..` entries.

Read coverage: complete file read, 448 lines.

Key responsibilities:
- Verifies that the superblock root inode is allocated and a directory; can create a new root directory and update the primary superblock.
- Ensures `/lost+found` exists under root, creating and linking it if needed.
- Reconnects orphaned files or directories into `/lost+found` with names of the form `#<inode>`.
- Walks directory parent records built in pass 2 to mark connected directories, detect cycles, and graft disconnected subtrees into `/lost+found`.
- Repairs `..` dirents when recorded parent dirent and on-disk `..` disagree.
- Special-cases orphan directory members, adjusting in-memory link accounting because orphan dirs do not necessarily update child `..` entries.

Important entry points:
- `o2fsck_pass3()` is the pass driver.
- `check_root()` validates or recreates root.
- `check_lostfound()` validates or creates `/lost+found`.
- `o2fsck_reconnect_file()` links an inode into `/lost+found`.
- `connect_directory()` walks parent chains and handles disconnected/cyclic directory trees.
- `fix_dot_dot()` and `fix_dot_dot_dirent()` update `..` directory entries and link counts.

Dependencies:
- Uses dir-parent state from passes 1/2, inode count maps, libocfs2 inode allocation, directory initialization, link, lookup, delete, superblock write, and directory iteration APIs.

Risk and edge cases:
- Creating a new root updates both `fs_root_blkno` and superblock `s_root_blkno`; failure rolls back the in-memory value and deletes the newly allocated inode.
- `/lost+found` creation must update icount and dir-parent state because pass 2 already completed directory scanning.
- Cycle detection uses a monotonically increasing `loop_no` per parent-chain walk.
- `fix_dot_dot()` logs but does not fully mark the filesystem invalid if it cannot find a `..` entry.
