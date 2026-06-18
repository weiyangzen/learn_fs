# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsls.c

## Role

`ntfsls.c` implements the `ntfsls` utility. It mounts an NTFS volume read-only and lists a directory’s entries or a single file’s selected name.

## Command-Line Contract

Supported options include:

- `-p/--path PATH`, default `/`.
- `-a/--all`, `-s/--system`, `-x/--dos`.
- `-l/--long`, `-i/--inode`, `-F/--classify`.
- `-R/--recursive`.
- `-f/--force`, `-q`, `-v`, `-V`, `-h`.

If `-s` is not specified, the parser defaults to `-a`, so normal user entries are listed broadly while metadata MFT records below `FILE_first_user` are hidden.

## Control Flow

1. `main()` parses options and mounts the volume read-only, adding recovery mode if forced.
2. It opens `opts.path` with `ntfs_pathname_to_inode()`.
3. If the inode is a directory:
   - non-recursive mode calls `ntfs_readdir()` with `list_dir_entry()`;
   - recursive mode calls `readdir_recursive()`.
4. If the inode is a file, it chooses a preferred `$FILE_NAME` attribute and sends it through `list_dir_entry()`.
5. It closes the inode and unmounts the volume.

## Listing Behavior

`list_dir_entry()` converts NTFS Unicode names to the current locale, filters metadata/system records, filters namespace entries based on `-a` and `-x`, optionally appends `/` for directories, and prints either simple names, inode-prefixed names, or long-format rows.

Long format opens each listed inode, reads `$FILE_NAME` for last data-change time, and reads unnamed `$DATA` length for file size when the entry is not a directory.

## Recursive Traversal

`readdir_recursive()` maintains static list heads for queued directories and path components. It prints each directory header, lists entries, queues subdirectories, then descends by reopening subdirectories relative to the parent inode.

## Risk Areas

- Recursive traversal has no explicit depth limit or cycle detection.
- `list_dir_entry()` appends `/` with `sprintf()` into a `MAX_PATH` buffer, so an already maximum-length converted name can overflow.
- Long-format size reporting only considers unnamed `$DATA`; alternate data streams are not included.
- Error handling in `main()` has FIXME comments and ignores some `ntfs_readdir()` failures.
- Recursive state is stored in static locals, making the function unsuitable for reentrant use.
