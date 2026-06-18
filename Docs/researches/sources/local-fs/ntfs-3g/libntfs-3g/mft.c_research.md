# File Research: sources/local-fs/ntfs-3g/libntfs-3g/mft.c

## Purpose
Implements low-level MFT record IO, validation, layout/formatting, MFT bitmap growth, MFT data growth, MFT record allocation/freeing, and update sequence number adjustment.

## Main Interfaces
- `ntfs_mft_records_read()` and `ntfs_mft_records_write()` read/write MST-protected MFT records.
- `ntfs_mft_record_check()` validates MFT record structure and attribute ordering/sizes.
- `ntfs_file_record_read()` reads, validates, and sequence-checks a FILE record.
- `ntfs_mft_record_layout()` initializes an empty record in memory.
- `ntfs_mft_record_format()` writes a freshly laid-out record.
- `ntfs_mft_record_alloc()` allocates a base or extent MFT record.
- `ntfs_mft_record_free()` marks an MFT record free and clears its bitmap bit.
- `ntfs_mft_usn_dec()` decrements a record update sequence number.
- Internal helpers grow `$MFT/$BITMAP`, grow `$MFT/$DATA`, and initialize newly exposed records.

## Control Flow
MFT reads refuse records beyond initialized `$MFT/$DATA`, use `ntfs_attr_mst_pread()`, and leave records deprotected. Writes protect records, update `$MFT`, and mirror affected low-numbered records to `$MFTMirr`.

Allocation first searches `$MFT/$BITMAP` after reserved records or near a base inode for extents. If no free bit exists, it extends bitmap allocation/initialized size, extends `$MFT/$DATA`, formats newly initialized records, marks the chosen bit, reads and reformats the old record while preserving sequence/USN when possible, sets `MFT_RECORD_IN_USE`, creates an `ntfs_inode`, and attaches it for extent allocations. Errors attempt to undo bitmap bits, cluster allocations, runlists, mapping pairs, and attribute sizes.

Freeing clears in-use flag, increments sequence number, syncs the inode, clears the bitmap bit, then closes/releases the inode; rollback restores bitmap bit and old sequence on failure.

## Integration Points
Core dependencies include `attrib.c`, `bitmap.c`, `lcnalloc.c`, `runlist.c`, `inode.c`, and MST-protected attribute IO. The file manipulates `vol->mft_na`, `vol->mftbmp_na`, `vol->mftmirr_na`, `vol->free_mft_records`, and `vol->mft_data_pos`.

## Risks and Invariants
- Records 0-23 are reserved; normal allocation starts at `RESERVED_MFT_RECORDS` 64 in this code.
- MFT extents have special placement rules to avoid circular dependency where extents are needed to find themselves.
- Several failure paths log “Leaving inconsistent metadata. Run chkdsk.” if rollback cannot fully restore on-disk state.
- `$MFTMirr` write failure is logged as needing chkdsk.
- `ntfs_mft_rec_init()` appears to return `-1` even after updating sizes; it is only used in the special `$MFT` extent path and warrants scrutiny.
