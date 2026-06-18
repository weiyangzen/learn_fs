# File Research: sources/local-fs/ntfs-3g/libntfs-3g/mst.c

## Purpose
Implements NTFS multi-sector transfer fixup handling for protected records such as MFT records and logfile pages.

## Main Interfaces
- `ntfs_mst_post_read_fixup_warn()` validates and deprotects a record after read, optionally warning.
- `ntfs_mst_post_read_fixup()` calls the warning variant with warnings enabled.
- `ntfs_mst_pre_write_fixup()` applies update sequence protection before write.
- `ntfs_mst_post_write_fixup()` restores original sector tails in memory after write protection.
- Internal `is_valid_record()` validates size, USA offset/count, and sector alignment.

## Control Flow
Post-read validation checks the USA header, compares each protected sector tail to the update sequence number, marks the record `BAAD` on incomplete transfer, and restores saved sector tails from the USA array. Pre-write increments the USN cyclically, stores original sector tails in the USA, and writes the USN into each tail.

## Integration Points
Used by MFT and logfile attribute IO. Depends on NTFS layout definitions and logging.

## Risks and Invariants
- Record size must be an NTFS block-size multiple.
- USA must fit before the last word in the first sector.
- USN skips `0` and `0xffff`.
- `ntfs_mst_post_write_fixup()` assumes a successful preceding pre-write fixup and performs no validation.
