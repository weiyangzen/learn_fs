# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmove.c

## Role

`ntfsmove.c` implements `ntfsmove`, a quarantined/experimental utility intended to relocate non-resident file data runs on an NTFS volume.

## Command-Line Contract

Usage is `ntfsmove [options] device file`.

Location options are mutually exclusive:

- `-S/--start`
- `-B/--best`
- `-E/--end`
- `-C/--cluster NUM`

Other options:

- `-D/--no-dirty`
- `-n/--no-action`
- `-f/--force`
- `-q`, `-v`, `-V`, `-h`

If no location is supplied, `--best` is selected.

## Control Flow

1. `parse_options()` captures device, file, location, mount, logging, and dirty-flag options.
2. `main()` mounts the volume, read-only for `--no-action` and recovery-capable for `--force`.
3. It resolves the target file path to an inode.
4. `move_file()` rejects unsafe files, enumerates all attributes, and relocates non-resident attributes.
5. `move_attribute()` decompresses mapping pairs and calls `move_datarun()` for each mapped run.
6. `move_datarun()` finds free space, rewrites mapping pairs, moves clusters, marks the inode dirty, and syncs it.
7. If bytes moved and dirty marking is not suppressed, `main()` writes `VOLUME_IS_DIRTY`.

## Data Movement Mechanics

- `find_unused()` scans `$Bitmap` for a contiguous free run.
- `move_runlist()` validates source clusters are allocated and destination clusters are free, sets destination bits, copies cluster data, and clears source bits.
- `resize_nonres_attr()` adjusts MFT record layout if the encoded mapping-pair array size changes.
- `ntfs_mapping_pairs_build()` writes the new mapping pairs into the attribute record.

## Safety Filters

`dont_move()` refuses to move metadata files, files with attribute lists, extent inodes lacking `$FILE_NAME`, and `ntldr`.

## Important Limitations And Bugs

- `find_unused()` ignores the requested location and flags, so `--start`, `--best`, `--end`, and `--cluster` do not actually control placement.
- `find_unused()` scans only `allocated_size / 8192` full chunks of the bitmap and can miss a trailing partial chunk.
- `move_datarun()` appears to update only the first runlist entry because it loops over the one-entry destination runlist while indexing the source runlist. Later source runs may be copied without having their mapping-pair LCN updated correctly.
- `--no-action` mounts read-only but does not short-circuit write-oriented bitmap, data-copy, and inode-sync code.
- The operation has crash windows: destination bitmap bits are set, data is copied, source bits are cleared, and only then are mapping pairs committed. Failures have little rollback.
- Several error paths leak temporary runlists or allocated buffers.
- The tool is quarantined in the build system, which is consistent with its incomplete and risky state.
