# File Research: sources/os/linux/linux/fs/ntfs3/fsntfs.c

## Role

Shared NTFS3 metadata and low-level filesystem utility layer. It defines well-known NTFS system names, handles NTFS record fixups, MFT and cluster allocation, $Extend children, $Secure descriptors, $Reparse/$ObjId indexes, block/run I/O helpers, filesystem dirty-state updates, deallocation, Windows filename validation, and volume-label updates.

## Key Responsibilities

- Defines constant NTFS names for core metadata files and indexes: `$MFT`, `$MFTMirr`, `$LogFile`, `$Volume`, `$AttrDef`, `$Bitmap`, `$BadClus`, `$Secure`, `$Extend`, `$ObjId`, `$Reparse`, `$UsnJrnl`, `$I30`, `$SII`, `$SDH`, `$SDS`, `$O`, `$Q`, `$R`, plus WOF compressed-data name when LZX/XPRESS support is enabled.
- `ntfs_fix_pre_write()` and `ntfs_fix_post_read()` implement NTFS multi-sector update-sequence fixups around MFT/index/log records.
- `ntfs_extend_init()` loads `$Extend` and discovers optional `$ObjId`, `$Quota`, `$Reparse`, and `$UsnJrnl` children.
- `ntfs_loadlog_and_replay()` loads `$LogFile`, temporarily wires `$MFT`, runs log replay, invalidates block-device cache, and clears initialized log content with `ntfs_bio_fill_1()`.
- `ntfs_look_for_free_space()` and `ntfs_check_free_space()` coordinate cluster allocation against the volume bitmap, delayed allocation reservations, and the MFT zone.
- MFT allocation flow:
  - `ntfs_extend_mft()` grows `$MFT::$DATA` and `$MFT::$BITMAP`.
  - `ntfs_look_free_mft()` reserves records for the MFT itself or general use.
  - `ntfs_mark_rec_free()` frees record numbers and updates search hints.
  - `ntfs_clear_mft_tail()` formats new records using `sbi->new_rec`.
  - `ntfs_refresh_zone()` recreates the MFT zone after the current MFT allocation.
- `ntfs_update_mftmirr()` copies the mirrored initial MFT records to `$MFTMirr`.
- `ntfs_bad_inode()` marks an NTFS inode bad without calling `make_bad_inode()` and marks the volume dirty on real metadata errors.
- `ntfs_set_state()` updates `$Volume::$VOLUME_INFORMATION` dirty flags for mount, clean unmount, and detected NTFS errors.

## I/O Helpers

- `ntfs_bread()` wraps `sb_bread_unmovable()` with bounds checks against `sbi->volume.blocks`.
- `ntfs_sb_write()` writes arbitrary byte ranges to block buffers, optionally synchronously, and can fill with `0xff` when `buf == NULL`.
- `ntfs_sb_write_run()`, `ntfs_bread_run()`, `ntfs_read_run_nb_ra()`, `ntfs_get_bh()`, `ntfs_write_bh()`, and `ntfs_read_write_run()` translate NTFS virtual byte offsets through runlists into block/page-cache I/O.
- `ntfs_read_bh_ra()` combines run reading with post-read fixup verification.
- `ntfs_bio_fill_1()` builds chained BIO writes to fill a logfile run with `0xff`.
- `ntfs_vbo_to_lbo()` maps VBO to LBO and reports contiguous byte count.

## Security and System Indexes

- `s_default_security` is the default self-relative Windows security descriptor used for new files when needed.
- `is_sd_valid()` validates self-relative security descriptors, SIDs, SACLs, and DACLs; `is_acl_valid()` validates ACL revision, sizing, and ACE boundaries.
- `ntfs_security_init()` loads `$Secure`, validates `$SDH` and `$SII` index roots, initializes their NTFS index descriptors, scans `$SII` for the next security id, and sets the next `$SDS` append offset.
- `ntfs_get_security_by_id()` looks up a descriptor in `$SII`, verifies the on-disk `$SDS` header matches the index entry, and returns a copied descriptor.
- `ntfs_insert_security()` deduplicates descriptors through `$SDH`, writes `$SDS` primary and mirror copies in 256 KiB buckets, and inserts matching `$SII` and `$SDH` entries.
- `ntfs_reparse_init()` and `ntfs_objid_init()` initialize `$Extend/$Reparse:$R` and `$Extend/$ObjId:$O` indexes.
- `ntfs_objid_remove()`, `ntfs_insert_reparse()`, and `ntfs_remove_reparse()` maintain object-id and reparse indexes.

## Allocation and Names

- `mark_as_free_ex()` frees clusters in the used bitmap, optionally discards/unmaps them, detects double-free corruption, and can grow the MFT zone.
- `run_deallocate()` frees all non-sparse extents in a runlist.
- `valid_windows_name()` rejects control characters, Windows-forbidden characters, trailing space/dot, and reserved DOS device names such as `CON`, `NUL`, `AUX`, `PRN`, `COM1`-`COM9`, and `LPT1`-`LPT9`.
- `ntfs_set_label()` converts a user label to UTF-16, replaces `$Volume::$VOLUME_NAME`, updates cached label text, and writes the volume inode.

## Dependencies

Uses NTFS3 core headers `debug.h`, `ntfs.h`, and `ntfs_fs.h`; Linux block, buffer-head, NLS, filesystem, kernel, and BIO APIs. It depends heavily on runlist, attribute, MFT-record, index, bitmap-window, and logfile replay helpers implemented elsewhere in the NTFS3 driver.

## Research Notes

This file is the driver’s central metadata service layer. It is security- and corruption-sensitive: record fixups, descriptor validation, allocation bitmaps, MFT growth, and dirty-volume state all defend against or respond to inconsistent on-disk metadata.
