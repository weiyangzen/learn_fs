# File Research: sources/local-fs/xfsprogs/repair/phase2.c

## Role

`phase2.c` implements phase 2: set up libxfs buffer-cache use, handle the log, scan AG freespace and inode maps, ensure root/metadata inode chunks exist, discover metadata inodes, and apply requested feature upgrades.

## Log Handling

`zero_log` initializes log structures, finds log head/tail, and enforces safe behavior:

- If log head/tail cannot be found, repair exits unless no-modify or explicit log zap allows proceeding.
- If the log contains unreplayed metadata, repair requires mounting to replay it unless `-L` or no-modify is used.
- If `zap_log` is set and modification is allowed, clears the log.
- Seeds `libxfs_max_lsn` for v5 filesystems.

The dummy `xlog_recover_do_trans` disables transaction replay in repair context.

## Feature Upgrade Helpers

The file supports adding:

- Inode btree counts.
- Bigtime timestamps.
- Nrext64 extent counters.
- Exchange-range support.

Each helper validates prerequisite features and exits cleanly when the feature already exists or cannot be added.

`install_new_geometry` temporarily installs the upgraded superblock to validate minimum log size and root inode location, then restores and reinstalls state cleanly.

The free-space upgrade check scaffolding exists, but `need_check_fs_free_space` currently returns false.

`upgrade_filesystem` writes the upgraded primary superblock immediately when modifying, setting `features_changed`.

## Phase 2 Flow

`phase2`:

- Calls `set_mp` so buffer cache routines can operate.
- Logs whether the filesystem uses an internal or external log.
- Retains the primary superblock buffer if writeback hooks require it.
- Processes the log.
- Scans AG freespace and inode maps via `scan_ags`.
- Ensures the root inode chunk exists in the in-core inode tree.
- Marks root, metadir root, realtime bitmap, and realtime summary inodes used/metadata as appropriate.
- Marks corresponding inode blocks in the block map if the chunk had to be synthesized.
- Discovers rtgroup metadata inodes.
- Discovers quota inodes for metadir quota filesystems.
- Applies feature upgrades.

## Interactions

Phase 2 seeds the in-core inode map and block map that `dinode.c`, `dir2.c`, and phase 4 rely on. It is the point where superblock-level feature additions are made durable before later rebuild work.
