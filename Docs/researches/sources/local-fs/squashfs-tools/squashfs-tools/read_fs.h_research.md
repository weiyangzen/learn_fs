# File Research: sources/local-fs/squashfs-tools/squashfs-tools/read_fs.h

Declares append-mode filesystem reading APIs: `read_super()` and the large `read_filesystem()` entry point.

`read_filesystem()` returns preserved table/cache data, counts, root inode/directory metadata, fragment table, inode lookup table, and accepts a callback for existing root directory entries.
