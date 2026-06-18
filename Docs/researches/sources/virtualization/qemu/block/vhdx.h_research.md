# File Research: sources/virtualization/qemu/block/vhdx.h

`vhdx.h` defines the VHDX on-disk structures, constants, shared driver state, and cross-file function prototypes used by `vhdx.c`, `vhdx-log.c`, and `vhdx-endian.c`.

Header-section constants describe the fixed first MiB: file identifier at offset 0, two 64 KiB header blocks, two region table blocks, and `VHDX_HEADER_SECTION_END`. `VHDXFileIdentifier`, `MSGUID`, `VHDXHeader`, `VHDXRegionTableHeader`, and `VHDXRegionTableEntry` model the file signature, Microsoft GUID layout, redundant headers, and region table records. The header uses CRC32C over a 4 KiB header area even though the packed header struct is smaller.

Log constants and structs define 1 MiB minimum log size, 4 KiB log sectors, log entry headers, descriptors, and data sectors. Log descriptors can be zero descriptors or data descriptors; data descriptors store the first 8 and last 4 bytes of a 4 KiB sector in the descriptor while the middle 4084 bytes live in a `VHDXLogDataSector`.

BAT constants define payload and sector-bitmap states, maximum sectors per block, bit masks for state and file offset, and `VHDXBatEntry`. Payload states include not present, undefined, zero, unmapped, fully present, and partially present. File offsets occupy the upper bits in 1 MiB units/alignment semantics.

Metadata structs define the metadata table header/entries and required metadata payloads: file parameters, virtual disk size, page 83 data, logical/physical sector sizes, and parent locator structures. Flags distinguish user metadata, virtual-disk metadata, and required metadata. VHDX supports up to 64 TiB virtual disk size and block sizes from 1 MiB to 256 MiB.

`VHDXMetadataEntries` stores recognized metadata table entries and a bitmask of presence. `VHDXLogEntries` stores circular-log runtime state: offset, length, write/read indexes, allocated header buffer, descriptor buffer, sequence, and tail. `VHDXRegionEntry` is an in-memory overlap-check list node. `BDRVVHDXState` is the main per-node state: coroutine mutex, active header index and two headers, region table entries, metadata, file parameters, block/sector/chunk sizing and shift caches, BAT entries and offset, first-visible-write flag, session GUID, log state, parent locator state, migration blocker, log-replayed flag, and registered regions.

The header also declares shared functions:
- GUID, checksum, and header update helpers from `vhdx.c`.
- Log parse/write/flush helpers from `vhdx-log.c`.
- Endian import/export helpers from `vhdx-endian.c`.
- `vhdx_user_visible_write()` for log code to trigger first-write header updates.

Inline GUID conversion helpers convert only `data1`, `data2`, and `data3`, preserving `data4` byte order. This is essential because MS GUIDs are not just raw 16-byte little-endian integers.
