# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscat.c

## Role

`ntfscat.c` implements the `ntfscat` command-line utility. It mounts an NTFS volume read-only, opens a file by path or MFT inode number, opens a selected attribute, and streams its bytes to stdout.

## Control Flow

1. `main()` installs stderr logging and calls `parse_options()`.
2. After successful parsing, it sets locale and mounts the volume read-only with `utils_mount_volume()`. `--force` maps to `NTFS_MNT_RECOVER`.
3. It opens the target inode via `ntfs_inode_open()` for `-i` or `ntfs_pathname_to_inode()` for a pathname. On Windows builds, the pathname is converted through `ntfs_utils_unix_path()`.
4. It chooses `AT_DATA` by default or the parsed `opts.attr`, then calls `cat()`.
5. It closes inode and unmounts the volume.

## Option Parsing

- `parse_attribute()` accepts symbolic NTFS attribute names with or without leading `$`, or numeric ids in decimal/octal/hexadecimal.
- `parse_options()` accepts `-a`, `-n`, `-i`, `-f`, `-h`, `-q`, `-V`, `-v`, and undocumented `-r/--raw`.
- It enforces one device, exactly one file or inode selector, and disallows quiet plus verbose together.
- Attribute names are converted from multibyte strings to NTFS Unicode via `ntfs_mbstoucs()`.

## Data Streaming

- `cat()` allocates a 4096-byte buffer and opens the requested attribute with `ntfs_attr_open()`.
- For normal reads it uses `ntfs_attr_pread()`.
- For fixup-protected records, it uses `ntfs_attr_mst_pread()` unless `--raw` is set:
  - MFT data for inode numbers below 2 uses `vol->mft_record_size`.
  - `$INDEX_ALLOCATION` uses the index block size read from the inode's `$INDEX_ROOT`.
- Output is written with `fwrite()` and failures are logged.

## Important Dependencies

The utility depends on ntfs-3g volume mounting, inode/path lookup, attribute open/read, MST-protected reads, option/logging utilities, and NTFS Unicode conversion.

## Notable Limitations And Risk Areas

- The `--raw` option exists in code but is intentionally not documented because compressed-file raw display does not work as intended.
- `index_get_size()` assumes a resident `$INDEX_ROOT` exists for index-allocation sizing; if absent, it returns zero and `cat()` falls back to plain reads.
- The tool writes arbitrary attribute bytes to stdout, so binary output is expected.
