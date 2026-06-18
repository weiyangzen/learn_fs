# File Research: sources/local-fs/xfsprogs/mkfs/proto.c

## Purpose
Implements `mkfs.xfs` filesystem population from either a legacy protofile or a source directory tree. It creates the root inode, optional metadata directory, realtime metadata inodes, regular files, directories, symlinks, special files, xattrs, parent pointers, and inherited root fsxattr settings.

## Key Elements
`setup_proto` classifies no input as a default root-directory protofile, regular input as an in-memory protofile, and directory input as `PROTO_SRC_DIR`. `parse_proto` dispatches to proto parsing or directory traversal and applies `slashes_are_spaces` and `preserve_atime`.

Protofile parsing uses `getstr`, `getnum`, `parseproto`, and type format strings for regular, reserved/preallocated, block, char, directory, symlink, and FIFO entries. It creates inodes through `creatproto`, links them with `newdirent`, and writes file data and xattrs after committing the initial inode/link transaction.

Directory population uses `populate_from_dir`, `walk_dir`, `handle_direntry`, `create_directory_inode`, and `create_nondir_inode`. It preserves uid/gid, mode, mtime, optional atime, file contents, xattrs, fsxattr-derived inode flags, and hardlinks via a growable source-inode to destination-inode tracker.

Realtime initialization is split across non-rtgroup and rtgroup paths. It creates rt bitmap/summary or rtgroup metadata inodes and frees realtime extents into the allocator, with special handling for realtime superblock and zoned filesystems.

## Dependencies
Depends heavily on libxfs transaction, inode, directory, symlink, xattr, realtime, parent-pointer, and allocation APIs. Also uses POSIX directory/stat/open/read/lseek/xattr/resource APIs and Linux xattr constants.

## Behavior/Risks
File data copying preserves sparse holes with `SEEK_DATA`/`SEEK_HOLE` and rounds data ranges to filesystem block boundaries to avoid partial-block corruption. Realtime regular-file creation from protofile content is rejected.

Directory-tree mode supports sockets as XFS directory entries but does not copy socket payloads. Hardlink tracking is keyed by source inode number only, so unusual traversals across multiple source devices with colliding inode numbers could misidentify hardlinks. Protofile names are tokenized by whitespace unless `slashes_are_spaces` rewrites slash characters in entry names.
