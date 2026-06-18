# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/mr.c

## Purpose
Memory registration lifecycle for SMBDirect RDMA read/write. This is primarily used by the SMB client side to expose local buffers to the peer via SMBDirect buffer descriptors.

## MR Pool Creation/Destruction
- `smbdirect_connection_create_mr_list()` requires nonzero negotiated responder resources and allocates `responder_resources * 2` MRs.
- Each `smbdirect_mr_io` gets:
  - kref and mutex
  - `ib_alloc_mr()` with negotiated MR type and `max_frmr_depth`
  - scatterlist array sized to `max_frmr_depth`
  - state `SMBDIRECT_MR_READY`
- `smbdirect_connection_destroy_mr_list()` splices the global MR list, disables each MR, detaches it from the socket, and drops the connection reference.
- `smbdirect_mr_io_disable_locked()` deregisters the MR, unmaps DMA SGs if present, frees the SGL, clears fields, and marks disabled.

## MR Acquisition
- `smbdirect_connection_get_mr_io()` waits for ready MR count while connected, scans the MR list for `SMBDIRECT_MR_READY`, marks it registered, takes a kref, decrements ready count, and increments used count.

## Registration
- `smbdirect_connection_register_mr_io()`:
  - checks iterator page count against `max_frmr_depth`
  - gets an MR
  - sets DMA direction based on SMBDirect operation
  - extracts iterator pages into the MR SG table via `extract_iter_to_sg()`
  - DMA maps SGs
  - maps SGs into the MR with `ib_map_mr_sg()`
  - updates rkey with `ib_update_fast_reg_key()`
  - posts `IB_WR_REG_MR`
- Registration completion only logs/schedules cleanup on failed CQ status; normal path relies on WR ordering before peer-visible I/O.

## Descriptor Export
- `smbdirect_mr_io_fill_buffer_descriptor()` fills `offset`, `token`, and `length` from the registered MR.
- If the MR is not registered, it fills sentinel max values.

## Deregistration
- `smbdirect_connection_deregister_mr_io()`:
  - disables immediately if socket is no longer connected
  - if `need_invalidate`, posts `IB_WR_LOCAL_INV` and waits for completion
  - otherwise marks remote-invalidated MR invalidated
  - unmaps DMA SGs
  - returns MR to ready state, wakes waiters, decrements used count, and drops caller kref
- Local invalidation completion marks state invalidated and completes `invalidate_done`.

## Error Handling
- Registration/deregistration posting failures schedule socket cleanup.
- Kref release is coordinated while holding the MR mutex to allow detached but still referenced MRs during connection teardown.
