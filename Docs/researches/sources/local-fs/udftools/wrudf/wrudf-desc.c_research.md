# File Research: sources/local-fs/udftools/wrudf/wrudf-desc.c

## Purpose

`wrudf-desc.c` contains helper routines for UDF File Identifier Descriptors and File Entries. It creates FIDs and file entries, finds named entries in a directory, inserts and physically removes FIDs from directory data, and deletes FIDs with associated file-entry/data-space cleanup.

## FID Removal And Deletion

`removeFID()` physically removes an FID from a directory's linear `dir->data` buffer. It computes the padded FID length, subtracts it from the directory file entry's `informationLength`, moves following bytes down, and marks the directory dirty.

`deleteFID()` performs semantic deletion:

- Reads the target file entry through `readTaggedBlock()`.
- Releases the target file-entry block from the packet cache with `freeBlock()`.
- If `fileLinkCount > 1`, decrements it and either marks the block dirty on CD-RW or writes a replacement file entry and updates VAT on CD-R.
- If this is the final link on CD-R, it decrements the parent directory link count for directories and marks the VAT entry invalid.
- If this is the final link on CD-RW, it decrements LVID file/directory counts, frees file data extents based on the file entry allocation descriptor type, and marks the file-entry block free.
- Finally removes the FID from the containing directory.

The function explicitly does not implement extended allocation descriptors.

## FID Lookup

`findFileIdentDesc()` encodes the requested locale filename into UDF dchars and scans the directory's FID stream until `informationLength` or a terminal entry. It skips parent entries, reports indirect entries as unimplemented, fails on unknown tag identifiers, and returns the first FID with matching encoded name bytes.

## File Entry Creation

`makeFileEntry()` allocates a zeroed 2048-byte block and initializes a regular-file UDF File Entry:

- Descriptor tag identity/version/serial.
- ICB strategy type and default regular file type.
- User read/write/delete/change/execute permissions plus group/other read/execute.
- Link count, access/modification/attribute timestamps.
- Implementation identifier.
- Unique ID from the logical volume header, post-incremented.

Callers specialize the returned file entry for directories, VAT entries, allocation descriptor mode, sizes, and checksums.

## FID Creation And Insertion

`makeFileIdentDesc()` allocates a zeroed FID buffer, initializes tag identity/version/serial, file version, and default ICB extent length. For non-parent entries it encodes the provided locale name into UDF dchars, falling back to a one-byte placeholder if encoding fails.

`insertFileIdentDesc()` computes padded FID length, sets descriptor CRC length, recomputes checksum, grows the directory data buffer in 2048-byte increments if needed, appends the FID bytes, updates the directory file entry's `informationLength`, and marks the directory dirty.

## Cross-File Role

`wrudf-cmnd.c` uses these helpers for all create, copy, delete, overwrite, directory lookup, and insertion operations. `wrudf-cdr.c` uses `makeFileEntry()` for VAT file entries. The helpers depend on globals initialized in `wrudf.c`, especially `lvd`, `lvid`, `pd`, `vat`, `medium`, and `entityWRUDF`.

## Notable Details

Deletion behavior differs sharply between CD-R and CD-RW: CD-R cannot reclaim physical space and instead invalidates VAT entries or appends replacement file entries, while CD-RW frees bitmap blocks and extents.

The commented-out partition check in `deleteFID()` suggests incomplete enforcement around writable-partition boundaries.
