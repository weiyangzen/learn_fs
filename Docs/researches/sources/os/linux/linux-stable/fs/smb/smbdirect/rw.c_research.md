# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/rw.c

## Purpose
Server-side RDMA read/write execution against peer-provided SMBDirect buffer descriptors.

## Credit Accounting
- `smbdirect_connection_calc_rw_credits()` computes credits from local buffer page count and pages per RW credit.
- `smbdirect_connection_wait_for_rw_credits()` waits on RW credits while connected.

## SG Construction
- `smbdirect_connection_rdma_get_sg_list()` converts a kernel/vmalloc buffer into scatterlist entries using `vmalloc_to_page()` or `kmap_to_page()`.
- It validates nonzero size and enough entries for the page span.

## RDMA Execution
- `smbdirect_connection_rdma_xmit()`:
  - validates connected state and `max_read_write_size`
  - walks descriptor array, truncating final descriptor length to remaining buffer length when needed
  - calculates needed credits
  - waits for RW credits
  - allocates one `smbdirect_rw_io` per descriptor
  - allocates chained SG tables
  - builds SGs over local buffer spans
  - initializes `rdma_rw_ctx` with remote offset/token and direction
  - chains work requests in reverse order
  - posts the chain with `ib_post_send()`
  - waits for completion of the last message
  - destroys all RDMA RW contexts, frees SG tables, returns credits, and wakes waiters

## Completion Handling
- `smbdirect_connection_rdma_read_done()` and `_write_done()` call shared completion logic.
- Failed completions set `msg->error = -EIO`; non-flush failures schedule socket cleanup.
- Completion wakes the stack completion used by the synchronous transmit call.

## Notes
- `is_read` selects DMA direction:
  - true: local buffer receives data (`DMA_FROM_DEVICE`)
  - false: local buffer sends data (`DMA_TO_DEVICE`)
- Exported as `smbdirect_connection_rdma_xmit`.
