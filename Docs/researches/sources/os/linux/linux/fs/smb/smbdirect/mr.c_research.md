# File Research: sources/os/linux/linux/fs/smb/smbdirect/mr.c

Implements client-side memory registration objects used for SMB Direct RDMA read/write buffer descriptors.

Key functions:
- `smbdirect_connection_create_mr_list()` allocates `responder_resources * 2` MR objects, each with an `ib_mr` and scatterlist sized to `max_frmr_depth`, marks them ready, and increments the ready count.
- `smbdirect_connection_destroy_mr_list()` detaches all MRs from the socket list, disables each MR, clears socket ownership, and drops references safely under each MR mutex.
- `smbdirect_connection_get_mr_io()` waits for a ready MR while connected, marks it registered, takes a reference, decrements ready count, and increments used count.
- `smbdirect_connection_register_mr_io()` validates iterator page count, extracts iterator pages into an SG table, DMA maps the SG list, maps it into the MR, updates the rkey, posts `IB_WR_REG_MR`, and returns the MR to the caller for descriptor publication.
- `smbdirect_mr_io_fill_buffer_descriptor()` fills an SMB Direct buffer descriptor with MR iova/rkey/length when registered, or sentinel invalid values otherwise.
- `smbdirect_connection_deregister_mr_io()` locally invalidates when required, waits for invalidation completion, DMA-unmaps the SG list, returns the MR to ready state, wakes waiters, decrements used count, and drops the caller reference.

Important state and invariants:
- MR states are `READY`, `REGISTERED`, `INVALIDATED`, `ERROR`, and `DISABLED`.
- Each MR has a mutex plus kref. The connection owns one reference; active registrations take another.
- Destruction can detach an MR from the connection while a registration user still holds a reference; final free occurs only after disable and kref release.
- Local invalidation uses `IB_WR_LOCAL_INV`; remote invalidation paths can set the MR invalidated without posting local invalidation.
- `register_mr_io()` posts the registration WR but does not wait for its completion; ordering is relied on before later sends that expose the descriptor.

Dependencies:
- Uses iterator-to-SG extraction, RDMA MR APIs, DMA SG mapping, and `smbdirect_socket_schedule_cleanup()` for fatal registration/invalidation failures.
- Buffer descriptor type comes from public SMB Direct definitions.

Maintenance notes:
- Error handling must preserve kref/mutex discipline; `smbdirect_mr_io_free_locked()` expects the mutex held and may unlock/free the MR.
- `smbdirect_iter_to_sgt()` depends on `extract_iter_to_sg()` to hold or pin pages appropriately for the iterator type supplied by upper layers.
