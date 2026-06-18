# File Research: sources/virtualization/qemu/block/vhdx-endian.c

`vhdx-endian.c` contains import/export helpers for VHDX on-disk little-endian structures. VHDX files store all multi-byte fields little-endian, but Microsoft GUID fields require mixed treatment where `data1`, `data2`, and `data3` are endian-converted while `data4` remains byte-array data.

The file provides conversions for:
- `VHDXHeader`: signature, checksum, sequence, GUIDs, log version, version, log length, and log offset.
- `VHDXLogDescriptor`: descriptor signature, file offset, sequence number, and export of union payload fields (`trailing_bytes`/`leading_bytes`).
- `VHDXLogDataSector`: data signature and split sequence high/low.
- `VHDXLogEntryHeader`: log header signature, checksum, entry length, tail, sequence, descriptor count, log GUID, flushed file offset, and last file offset.
- `VHDXRegionTableHeader` and `VHDXRegionTableEntry`.
- `VHDXMetadataTableHeader` and `VHDXMetadataTableEntry`.

The helpers assert non-null pointers and mostly convert in place, except `vhdx_header_le_export()` copies from a host-order source header into a separate little-endian destination. These functions are used by `vhdx.c` and `vhdx-log.c` before validating, checksumming, writing headers, building logs, and parsing metadata.
