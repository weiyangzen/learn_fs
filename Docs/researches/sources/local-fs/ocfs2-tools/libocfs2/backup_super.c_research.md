# File Research: sources/local-fs/ocfs2-tools/libocfs2/backup_super.c

Manages OCFS2 backup superblock locations and contents.

`ocfs2_get_backup_super_offsets()` fills caller storage with backup superblock block numbers, using `fs->fs_blocksize` when available or byte-offset mode when `fs` is NULL. It stops at `OCFS2_MAX_BACKUP_SUPERBLOCKS` or when a computed block lies beyond the filesystem.

`ocfs2_set_backup_super_list()` optionally checks that target clusters are free if the backup-super feature is not already enabled, zeroes each target cluster, writes current superblock data to each backup location, then marks the clusters allocated. `ocfs2_clear_backup_super_list()` frees listed clusters only if the compat backup-super feature is enabled, avoiding accidental data free.

`ocfs2_refresh_backup_supers()` refreshes all feature-enabled backup supers; `ocfs2_read_backup_super()` validates the feature and backup index before reading. Legacy singular wrapper names forward to the newer `_list`/`_offsets` APIs.
