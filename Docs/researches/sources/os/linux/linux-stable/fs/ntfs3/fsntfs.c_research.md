# File Research: sources/os/linux/linux-stable/fs/ntfs3/fsntfs.c

## Role

Volume-wide NTFS3 support code. This file owns NTFS system names, multi-sector record fixups, log replay setup, cluster and MFT allocation, raw run I/O helpers, volume dirty-state updates, `$Secure` security descriptor management, `$Extend` reparse/object-id index setup, cluster deallocation, Windows filename validation, and label updates.

## Key Functions

- `ntfs_fix_pre_write()` and `ntfs_fix_post_read()` apply and validate NTFS update-sequence-array fixups for protected records.
- `ntfs_extend_init()` loads `$Extend` and caches `$ObjId`, `$Quota`, `$Reparse`, and `$UsnJrnl` inode references when present.
- `ntfs_loadlog_and_replay()` loads `$MFT`, invokes log replay for `$LogFile`, invalidates block-device cache afterward, and clears initialized logfiles by filling them with `0xff`.
- `ntfs_look_for_free_space()` allocates clusters from the volume bitmap, including special handling for MFT-zone allocations and MFT-zone shrinkage under space pressure.
- `ntfs_check_free_space()` estimates whether both requested data clusters and MFT records can fit while accounting for delayed allocation reservations.
- `ntfs_extend_mft()` grows `$MFT::$DATA` and `$MFT::$BITMAP`, refreshes the MFT zone, formats new empty records, and writes the updated MFT inode.
- `ntfs_look_free_mft()` allocates an MFT record, extending the MFT if necessary and falling back to reserved system records only in constrained cases.
- `ntfs_mark_rec_free()` releases an MFT bitmap bit and updates zone/next-free hints.
- `ntfs_clear_mft_tail()` formats newly available MFT records with the template record.
- `ntfs_refresh_zone()` rebuilds the MFT zone after the last MFT run.
- `ntfs_update_mftmirr()` copies mirrored MFT records from `$MFT` to `$MFTMirr`.
- `ntfs_bad_inode()` marks the NTFS inode bad and marks the volume dirty unless log replay is in progress.
- `ntfs_set_state()` updates the `$Volume` dirty flag in `ATTR_VOL_INFO`.
- `ntfs_bread()`, `ntfs_sb_write()`, `ntfs_sb_write_run()`, `ntfs_read_run_nb_ra()`, `ntfs_get_bh()`, `ntfs_write_bh()`, `ntfs_read_write_run()`, and `ntfs_vbo_to_lbo()` provide low-level block/run based I/O utilities.
- `ntfs_bio_fill_1()` writes `0xff` pages over an entire run list, used to reset initialized log data.
- `ntfs_new_inode()` allocates and initializes a new VFS/NTFS inode pair for a selected MFT record.
- `is_sd_valid()` validates relative Windows security descriptors and nested ACL/SID ranges.
- `ntfs_security_init()` loads `$Secure`, initializes `$SDH` and `$SII`, and computes the next security ID and SDS append offset.
- `ntfs_get_security_by_id()` resolves `$SII` entries to on-disk `$SDS` descriptors.
- `ntfs_insert_security()` deduplicates security descriptors through `$SDH`, appends new descriptors and their mirrored SDS copy, and inserts `$SII`/`$SDH` index entries.
- `ntfs_reparse_init()` and `ntfs_objid_init()` initialize `$Extend/$Reparse:$R` and `$Extend/$ObjId:$O` indexes.
- `ntfs_insert_reparse()` and `ntfs_remove_reparse()` maintain reparse-point index entries.
- `mark_as_free_ex()` and `run_deallocate()` free allocated clusters, optionally discarding them and adjusting the MFT zone.
- `valid_windows_name()` rejects Windows-forbidden characters, trailing space/dot names, and reserved DOS device names.
- `ntfs_set_label()` replaces the volume label attribute and updates the cached label.

## Synchronization and State

- Cluster allocation uses `sbi->used.bitmap.rw_lock` with `BITMAP_MUTEX_CLUSTERS`.
- MFT record allocation uses `sbi->mft.bitmap.rw_lock` with `BITMAP_MUTEX_MFT`.
- File run modifications use `ni->file.run_lock`.
- Security, reparse, object-id, and dirty-state changes use nested NTFS inode mutex classes.
- Dirty volume state is persisted through `$Volume` and cached in `sbi->volume.flags` / `real_dirty`.

## Research Notes

This is the NTFS3 volume services hub. It connects bitmap allocation, metadata file growth, system-file indexes, security descriptor storage, and raw block I/O. Several paths deliberately mark the volume dirty rather than attempting silent recovery when metadata invariants fail.
