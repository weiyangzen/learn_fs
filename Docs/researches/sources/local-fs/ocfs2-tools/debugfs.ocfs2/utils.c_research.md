# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/utils.c

## Role

`utils.c` provides shared helpers for `debugfs.ocfs2`: feature flag formatting, time formatting, pager integration, inode/path parsing, file extraction, recursive dumps, free-space analysis, debugfs discovery, string-list management, and extent/chain traversal.

## Filespec And Output Helpers

It decodes angle-bracket inode/lockname strings, resolves `//` paths to the system directory, opens `$PAGER` for interactive output, formats inode permissions and times, and normalizes GLib split arguments by moving empty strings to the end.

## File Extraction

`dump_file()` reads a cached inode, writes regular file contents in 1 MiB chunks, handles symlinks, and optionally preserves mode, ownership, and timestamps. `rdump_inode()` recursively recreates regular files, symlinks, and directories under a native destination directory.

## Metadata Traversal

`traverse_extents()` recursively dumps extent trees. `traverse_chains()` walks chain records and either dumps group descriptors, dumps free-bit summaries, or writes computed contiguous-free-bit values back into group descriptors.

## Live Debugfs Support

`get_debugfs_path()` validates `/sys/kernel/debug` or `/debug` as debugfs. `open_debugfs_file()` opens debugfs files under subsystem/UUID paths and maps common failures to OCFS2/o2cb error codes.

## Risk Areas

Some helpers write to native files/directories during dump extraction, and `RECORD_GD_FREE_BITS` writes metadata through libocfs2. Several operations rely on global `gbls.fs` even when an `fs` parameter is passed.
