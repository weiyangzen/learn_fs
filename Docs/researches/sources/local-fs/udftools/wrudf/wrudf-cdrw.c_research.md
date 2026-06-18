# File Research: sources/local-fs/udftools/wrudf/wrudf-cdrw.c

## Purpose

`wrudf-cdrw.c` is the shared low-level I/O layer for rewritable UDF media, append-only CD-R media, and disk-image testing. For CD-RW it implements a small 32-sector packet buffer cache, space bitmap allocation, sparing-table support, descriptor checksum/CRC helpers, extent reads/writes, and device initialization/finalization.

## Packet Buffer Model

The file defines four normal packet buffers plus one special buffer:

- `struct packetbuf` tracks `inuse` bits, `dirty` bits, buffer number, packet start block, and a 32-sector memory buffer.
- `findBuf()` locates a cached packet by aligned packet start.
- `getFreePacketBuffer()` chooses a clean unused buffer, or writes a dirty unused buffer before reuse. If every buffer is in use, it returns `NULL` after printing a panic-style message.
- `readPacket()` reads a 32-sector packet from the device or disk image, applying sparing-table remapping.
- `writePacket()` writes a 32-sector packet, verifies real optical writes by strict reread, and creates a new sparing-table mapping on retry.

`readBlock()`, `dirtyBlock()`, `freeBlock()`, and `writeBlock()` expose block-sized operations over the packet cache. CD-R bypasses the cache and delegates reads to `readCDR()`.

## Space Allocation

`markBlock()` updates the UDF space bitmap and the free-space count stored in the LVID partition data. `ALLOC` clears a bitmap bit and decrements free count; `FREE` sets the bit and increments free count.

`getExtents()` allocates short allocation descriptors. For CD-R it returns a synthetic extent at the current append position. For CD-RW it scans `spaceMap->bitmap`, coalesces free blocks into up to 32 extents, and returns the byte length of the descriptor array.

`freeShortExtents()` and `freeLongExtents()` mark previously allocated short or long extents free. Long extents are required to belong to the writable partition.

`getUnallocSpaceExtent()` allocates from the Unallocated Space Descriptor, used primarily for extending the Logical Volume Integrity Descriptor sequence.

## Descriptor And Timestamp Helpers

`setChecksum()` computes a descriptor CRC over the descriptor body and computes the 16-byte UDF tag checksum with the checksum byte cleared.

`updateTimestamp()` fills the global UDF `timeStamp` from either current time or a provided `time_t` plus microsecond value, including local timezone offset and subsecond fields.

`readTaggedBlock()` reads a descriptor, tolerates all-zero non-UDF blocks and sparing-table blocks with tag identifier zero, verifies the tag checksum, verifies descriptor CRC, and returns the block pointer.

## Address Translation And Sparing

`getPhysical()` handles three address modes:

- `ABSOLUTE` returns the block number unchanged.
- A virtual partition maps through `vat[lbn]`.
- Other partitions add `pd->partitionStartingLocation`.

`lookupSparingTable()` maps packet starts through the sparing table when present. `newSparingTableEntry()` inserts a new sorted sparing entry, preserving the next available mapped location and marking the table dirty. `updateSparingTable()` writes all sparing-table copies listed in the sparable partition map without verification to avoid recursively changing the table.

## Extent I/O

`readExtents()` and `writeExtents()` read or write byte streams described by either short or long allocation descriptors. They walk descriptor chains, switch to the next descriptor at extent boundaries, and operate in 2048-byte block units.

These helpers are used for directory data, VAT payloads, and file data that is not embedded in a file entry.

## Initialization

`initIO()` detects whether the path is a regular file disk image or an optical device:

- Disk images are opened read-write and classified heuristically as CDR or CDRW based on the descriptor identifier at block 512.
- Optical devices are opened nonblocking read-only, checked with `CDROM_DRIVE_STATUS`, queried with `read_discinfo()` and `read_trackinfo()`, and classified by the erasable bit.
- CD-RW must use fixed 32-sector packets. CD-R must be variable-packet appendable with a valid next writable address.
- The function derives `trackStart`, `trackSize`, and `sectortype`, reads error-recovery and cache mode pages, and sets write parameters for either fixed-packet CD-RW or variable-packet CD-R.

For CD-RW, it allocates packet buffers and a 32-sector verification buffer. For all modes it allocates `blockBuffer`.

## Finalization

`closeIO()` writes any dirty unused CD-RW packet buffers, reports still-in-use or dirty buffers, frees packet and verification buffers, synchronizes real device cache, closes the device, and returns success.

## Notable Details

The code assumes 2048-byte logical blocks and 32-sector CD-RW packets throughout. Disk-image support is built into the same paths, including optional debug sparing.

Some checks compare `device` rather than `devicetype` against `DISK_IMAGE` in `setStrictRead()` and `syncCDR()` is implemented elsewhere with similar concerns. Since `DISK_IMAGE` is a sentinel devicetype, not a file descriptor, those branches are fragile.
