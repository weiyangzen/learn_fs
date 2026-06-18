# File Research: sources/os/linux/linux/fs/exfat/exfat_fs.h

## Purpose
Central private header for the Linux exFAT driver. It defines in-memory structures, type constants, conversion macros, mount options, inode/superblock private state, inline helpers, and cross-file prototypes.

## Main Contents
- Logical dentry type constants such as `TYPE_FILE`, `TYPE_DIR`, `TYPE_STREAM`, `TYPE_EXTEND`, bitmap/upcase/volume/vendor types.
- Size and conversion macros for clusters, blocks, dentries, FAT entries, and allocation bitmap offsets.
- Core structures: `exfat_uni_name`, `exfat_chain`, `exfat_hint`, `exfat_hint_femp`, `exfat_entry_set_cache`, `exfat_dir_entry`, `exfat_mount_options`, `exfat_sb_info`, `exfat_inode_info`.
- Inline helpers: `EXFAT_SB`, `EXFAT_I`, forced-shutdown test, mode/attribute conversion, cluster/sector conversion, cluster validity, ondisk-size calculation, `exfat_cluster_walk`, and `exfat_chain_advance`.
- Prototypes for super, FAT/bitmap, file, namei, cache, dir, inode, NLS, and misc modules.

## Integration Role
This header is the contract tying all exFAT `.c` files together. It exposes shared locking state (`s_lock`, `bitmap_lock`), allocation state (`vol_amap`, `used_clusters`, `clu_srch_ptr`), directory/inode hints, and file-operation declarations.

## Notable Invariants And Risks
- `ALLOC_NO_FAT_CHAIN` means cluster traversal is arithmetic; `ALLOC_FAT_CHAIN` means FAT lookup.
- Directory entry sets are bounded by `ES_MAX_ENTRY_NUM` and cached across up to `DIR_CACHE_SIZE` sectors.
- Mode/attribute conversion is mount-option dependent and intentionally limited by exFAT metadata capabilities.
