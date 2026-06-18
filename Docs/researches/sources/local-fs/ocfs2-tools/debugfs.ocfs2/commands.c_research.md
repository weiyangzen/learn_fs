# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/commands.c

## Role

`commands.c` is the command dispatcher and command implementation layer for `debugfs.ocfs2`. It owns the global debugfs session state (`gbls`), maps command names to handlers, opens/closes OCFS2 devices or image files, translates user file specifications, and invokes the lower-level dump/search/journal helpers.

## Command Surface

The command table implements filesystem inspection and diagnostic commands including `open`, `close`, `stats`, `stat`, `ls`, `cat`, `dump`, `rdump`, `bmap`, `icheck`, `locate`/`ncheck`/`findpath`, `logdump`, `hb`, `slotmap`, `group`, `grpextents`, `gd_free_bits`, `extent`, directory-index commands, xattr/refcount commands, live filesystem/DLM lock dump commands, network stats, `controld dump`, `lcd`, `cd`, `chroot`, `curdev`, `help`, and quit aliases.

## Device And Filespec Handling

`do_open()` opens a block device or `o2image` file with read-only or read-write flags, permits heartbeat devices, disables ECC checks, handles backup superblock selection, allocates a block buffer, caches root/system/heartbeat/slotmap/journal block numbers, and resets current working directory to `/`.

Filespecs can be pathnames, relative names, system-directory paths via `//`, raw inode forms like `<123>`, or lock names decoded through libocfs2. Most commands validate that translated block numbers are below `gbls.max_blocks`.

## Metadata And Data Operations

The file reads inodes, directories, extent blocks, group descriptors, slot maps, heartbeat files, journals, xattr blocks, refcount trees, and directory-index structures, then delegates formatting to `dump.c` and traversal helpers in `utils.c`.

`dump` and `cat` use `dump_file()`. `rdump` recursively extracts a subtree to a mounted native directory. `bmap` walks extent trees to translate logical file blocks to physical block numbers. `icheck` delegates reverse block ownership lookup to `find_block_inode()`.

## Live Kernel Diagnostics

`fs_locks`, `dlm_locks`, and `net_stats` can read live debugfs files or saved captures. They support filtering lock names, dumping LVBs, showing only busy locks, and repeated network-stat sampling.

## Mutation

Most commands are read-only, but `gd_free_bits -s` can record computed contiguous free-bit information back into group descriptors and therefore requires the debugfs process to have opened the filesystem with `-w`.

## Risk Areas

Command parsing is simple GLib whitespace splitting, so quoting is not shell-like. The code depends heavily on global mutable state and a single reusable block buffer. Write-capable paths are intentionally narrow but operate on metadata, so `-w` use is risky on mounted or damaged filesystems.
