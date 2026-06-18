# File Research: sources/os/linux/linux-stable/fs/nfsd/blocklayoutxdr.c

Purpose: Encodes and decodes pNFS block/SCSI layout opaque XDR payloads for NFSD.

Key responsibilities:
- Encodes layoutget extent arrays:
  - deviceid,
  - file offset,
  - extent length,
  - storage offset,
  - extent state.
- Encodes getdeviceinfo volume arrays for simple block and SCSI volumes.
- Handles zero `gd_maxcount` by returning zero-length notification marker per RFC guidance.
- Decodes block layoutcommit updates:
  - validates exact expected payload size,
  - decodes deviceid and extent fields,
  - enforces file/storage offset and length alignment,
  - requires `PNFS_BLOCK_READWRITE_DATA`,
  - produces iomap array.
- Decodes SCSI layoutcommit updates as aligned file offset/length ranges.

Integration:
- Called by `blocklayout.c` layout ops.
- Uses NFSD XDR helpers, SUNRPC XDR streams, and iomap structures.

Risks and notes:
- Allocation failure maps to `nfserr_delay`.
- Bad payload length or decode failure maps to `nfserr_bad_xdr`; alignment and invalid extent state map to `nfserr_inval`.
