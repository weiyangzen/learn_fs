# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/main.c

Implements the `fsck_ext2fs` command entry point and phase driver.

Main behavior:
- Parses options for alternate superblock, debug, force check, lost+found mode, assume-no, preen, and assume-yes.
- Calls shared root/device setup, syncs before checking, installs interrupt/quit handlers, and checks exactly one filesystem operand.
- Maintains all major global fsck state: buffers, ext2 superblock, duplicate lists, inode caches, maps, counters, flags, and file descriptors.

`checkfilesys` flow:
1. Runs `setup` and skips clean filesystems when allowed.
2. Phase 1: scans inodes, block usage, sizes, and initial state.
3. Phase 1b: rescans for duplicate block owners if duplicates were found.
4. Phase 2: checks pathnames and directory contents.
5. Phase 3: checks directory connectivity.
6. Phase 4: checks reference counts and clears/reconnects unreferenced objects.
7. Phase 5: verifies group bitmaps and summary counts.
8. Prints file/block summary, updates fsck timestamps when modified, cleans up, and marks the filesystem clean when appropriate.

Root handling:
- If the root filesystem was modified and mounted read-only, attempts a mount update/reload.
- Otherwise requests reboot semantics via exit code when needed.

This file coordinates the ext2 checker lifecycle; the pass files contain the detailed checks.
