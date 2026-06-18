# File Research: sources/os/linux/linux/fs/smb/smbdirect/rw.c

Implements server-side RDMA read/write transfer execution against peer-provided SMB Direct buffer descriptors.

Key functions:
- `smbdirect_connection_wait_for_rw_credits()` consumes RDMA RW credits using the generic socket credit waiter.
- `smbdirect_connection_calc_rw_credits()` computes required RW credits from local buffer page count and negotiated pages-per-credit.
- `smbdirect_connection_rdma_get_sg_list()` converts a kernel/vmalloc buffer into a scatterlist by walking pages.
- `smbdirect_connection_rw_io_free()` destroys the `rdma_rw_ctx`, frees chained SG tables, and frees the flexible IO object.
- `smbdirect_connection_rdma_xmit()` is the exported main operation. It validates connected state and max read/write size, walks buffer descriptors, clamps descriptor lengths to remaining buffer length, computes credits, waits for credits, builds one `smbdirect_rw_io` and `rdma_rw_ctx` per descriptor, chains WRs in reverse order, posts them, waits for completion, frees all contexts, restores credits, and returns completion error status.

Direction semantics:
- `is_read == true` uses `DMA_FROM_DEVICE` and RDMA read completion callback.
- `is_read == false` uses `DMA_TO_DEVICE` and RDMA write completion callback.
- Completion errors set `msg->error = -EIO`; non-flush failures schedule socket cleanup.

Important state:
- `rw_io.credits.count` limits concurrent RDMA RW contexts.
- Credits are always returned after the operation’s cleanup path.
- The function mutates descriptor lengths if a descriptor extends beyond the remaining requested buffer length.

Dependencies:
- Uses RDMA core `rdma_rw_ctx_*` helpers.
- Uses public `struct smbdirect_buffer_descriptor_v1`.
- Uses `smbdirect_get_buf_page_count()` from `socket.h`.

Maintenance notes:
- The log message after descriptor walking prints `buf_len` after it has been consumed down, which may be zero rather than original length.
- The implementation waits for one stack completion after posting the chained WR list and then reads the last message error; changes to multiple completion behavior should verify all contexts complete before free.
