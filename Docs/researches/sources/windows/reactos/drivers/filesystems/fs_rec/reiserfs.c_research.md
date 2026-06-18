# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/reiserfs.c

This file implements the ReiserFS recognizer. It reads the ReiserFS superblock at the fixed 64 KiB disk offset and checks the magic string.

`FsRecIsReiserfsVolume` compares `s_magic` against `REISER2FS_SUPER_MAGIC_STRING` for `MAGIC_KEY_LENGTH` bytes. The current check recognizes `ReIsEr2Fs`, not the older `ReIsErFs` or `ReIsEr3Fs` strings defined in the header.

`FsRecReiserfsFsControl` handles:
- `IRP_MN_MOUNT_VOLUME`: gets sector size, reads one sector at `REISERFS_DISK_OFFSET_IN_BYTES`, validates the superblock, and returns `STATUS_FS_DRIVER_REQUIRED` on match.
- `IRP_MN_LOAD_FILE_SYSTEM`: loads `\Registry\Machine\System\CurrentControlSet\Services\reiserfs`.

If sector-size discovery or the read path reports a device error on a floppy device, the recognizer returns `STATUS_FS_DRIVER_REQUIRED` to let the filesystem driver attempt handling.

Research notes:
- Several comments still say Btrfs; behavior is ReiserFS-specific.
- The recognizer reads only one sector, so it assumes the magic field is within that first sector of the superblock area.
- Magic matching is narrower than the header constants suggest.
