# File Research: sources/os/linux/linux/fs/nfsd/blocklayoutxdr.c

Encodes and decodes NFSD pNFS block/SCSI layout opaque XDR payloads.

Key behavior:
- `nfsd4_block_encode_layoutget()` encodes the layout body length, extent count, and each extent’s device ID, file offset, length, storage offset, and extent state.
- `nfsd4_block_encode_volume()` encodes either:
  - Simple block volumes with signature offset and opaque signature.
  - SCSI volumes with code set, designator type, designator, and persistent-reservation key.
- `nfsd4_block_encode_getdeviceinfo()` handles the RFC maxcount-zero case by returning a zero-length body, otherwise encodes all volumes and backfills total length and volume count.
- `nfsd4_block_decode_layoutupdate()` decodes block layoutcommit extent arrays, validates total length, allocates iomaps, checks file offset/length/storage offset block alignment, requires `PNFS_BLOCK_READWRITE_DATA`, and returns iomaps for commit.
- `nfsd4_scsi_decode_layoutupdate()` decodes SCSI layoutcommit ranges, validates encoded size, allocates iomaps, and checks offset/length alignment.

Important interactions:
- Shared by block layout and SCSI layout server operations in `blocklayout.c`.
- Produces and consumes opaque layout bodies used inside higher-level NFSv4.1 layoutget/getdeviceinfo/layoutcommit XDR.
