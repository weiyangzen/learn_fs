# File Research: sources/local-fs/e2fsprogs/misc/e4defrag.8.in

## Purpose
Manual page for `e4defrag`, an online defragmenter for extent-based ext4 files.

## Documented Interface
- `e4defrag [-c] [-v] target ...`

## Behavior Described
- Targets can be regular files, directories, or mounted ext4 block devices.
- Directory targets recursively defragment files inside.
- Device targets resolve the mount point and defragment files on that filesystem.
- Only extent-based ext4 files are supported.

## Options
- `-c`: report current and ideal fragmentation counts and a fragmentation score; does not defragment.
- `-v`: verbose per-file errors and before/after extent counts.

## Notes
- Does not support swap files, files in `lost+found`, or files using indirect blocks.
- Avoids crossing into other mounted filesystems.
- Can run on active files, but may cause page cache and I/O contention.
- Non-root users can defragment their own files, but score details are limited.
