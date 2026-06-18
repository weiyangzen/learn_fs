# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/vscsiif.h

Imported Xen public virtual SCSI frontend/backend protocol ABI.

Purpose:
- Defines Xen virtual SCSI request/response ring structures and scatter/gather segment layout.

Key content:
- Defines commands for SCSI CDB, abort, reset, and SG preset.
- Defines scatter/gather table size, max CDB size, and sense buffer size.
- Defines `vscsiif_segment_t`, `struct vscsiif_request`, `struct vscsiif_sg_list`, and `struct vscsiif_response`.
- Generates `vscsiif` ring types.

Integration:
- Not used by visible 9front Xen runtime code.
- Storage-related vendored protocol, but 9front’s active virtual storage code uses block `blkif`.

Risks/notes:
- Response includes large fixed reserved space and sense buffer; ABI size assumptions matter for ring layout.
- SG preset requires first fields to match main request layout.
