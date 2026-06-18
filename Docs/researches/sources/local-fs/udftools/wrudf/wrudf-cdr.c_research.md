# File Research: sources/local-fs/udftools/wrudf/wrudf-cdr.c

## Purpose

`wrudf-cdr.c` implements the append-only CD-R path for `wrudf`. It manages the Virtual Allocation Table (VAT), writes new physical sectors at the drive's next writable address, reads logical data through the VAT mapping, verifies written CD-R data, and writes a new VAT file entry when finalizing.

## Main State

The file-local state is:

- `blockBuffer`: one 2048-byte read/verify buffer.
- `newVATindex`: next logical VAT entry to allocate.
- `sizeVAT`: allocated VAT byte size.
- `prevVATlbn`: physical block number of the previous VAT file entry.
- `CDRuniqueID`: exported unique ID from the VAT file entry, later copied into the logical volume header by `wrudf.c`.

It uses global state from `wrudf.h`, including `vat`, `device`, `devicetype`, `pd`, `ti`, `lastTrack`, `sectortype`, `ignoreReadError`, and `medium`.

## VAT Allocation And Addressing

`newVATentry()` ensures there is spare VAT capacity for the allocation entries plus VAT trailer data, grows the VAT by one 2048-byte block when needed, records the current next writable physical location relative to the partition start, and returns the new virtual logical block index.

`getNWA()` returns the next writable address. For disk images it uses file length divided by 2048. For devices it refreshes `ti` through `read_trackinfo()` and returns `ti.nwa` only if `ti.nwa_v` is set, otherwise `INVALID`.

`readCDR()` maps logical block plus partition to a physical block through `getPhysical()`, then reads either from a disk image by `lseek`/`read` or from optical media with `readCD()`. It suppresses sense logging when `ignoreReadError` is set.

## Writing

`writeHD()` writes one 2048-byte block to a disk-image physical block. `writeCDR()` writes one 2048-byte block at `getNWA()`, either through `writeHD()` for images or `writeCD()` for devices, and returns the physical block written.

`syncCDR()` flushes device cache for real devices. `writeHDlink()` writes seven link blocks to disk images after CD-R-style writes, emulating the link-block behavior that real packet writing leaves between variable packets.

## Verification And Bad-Block Handling

`verifyCDR()` verifies a just-written file entry and its data extents using strict read settings. It walks long allocation descriptors and reads data blocks that are physically after the file entry. On read failure it calls `flagError()` to split the affected extent into good and bad ranges. Bad ranges are represented by extents whose logical block number is zero, then later reassigned to future rewrite locations.

If data verification succeeds, `verifyCDR()` verifies the file entry itself up to three times. A failed file-entry verification causes it to write a replacement file entry and update the VAT entry for the file entry's virtual logical block.

After any data verification failures, it rewrites allocation descriptors so bad ranges point to future physical blocks after the current NWA. The caller can then rewrite only the defective data ranges and the updated file entry.

## VAT Read/Write

`readVATtable()` finds the previous VAT file entry near the end of the appendable track, validates that it is a VAT file entry, records its unique ID, allocates the in-memory VAT, and reads either embedded VAT data or VAT data extents.

`writeVATtable()` appends the VAT trailer regid (`UDF_ID_ALLOC` plus UDF revision and OS identifiers), creates a VAT file entry with type `ICBTAG_FILE_TYPE_VAT15`, writes VAT payload blocks followed by the file entry, and verifies the whole written sequence. It retries up to eight times before reporting a failed VAT rewrite.

## Cross-File Role

`wrudf-cmnd.c` calls `newVATentry()`, `writeCDR()`, `verifyCDR()`, `getMaxVarPktSize()`, and `writeHDlink()` while copying files and updating directories on CD-R media. `wrudf.c` calls `readVATtable()` during initialization and `writeVATtable()` during finalization.

## Notable Details

`flagError()` performs in-place extent-array splitting with `memmove()` expressions that depend on fixed available descriptor capacity. The function is tightly coupled to the file-entry allocation descriptor area and assumes enough room for splits.

The CD-R path depends on long allocation descriptors because file data is written in physical partition space while file entries are addressed through virtual VAT space.
