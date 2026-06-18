# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_resource.h

## Purpose

Defines iSER memory-region pools, registered message/data buffer objects, work request tracking objects, cache constructors/destructors, and routines for allocating registered memory and registering in-place IDM buffers.

## Main Definitions

- Cache name length and default control/text PDU and data buffer lengths.
- `iser_mr_t`: IBT MR handle, virtual address, length, lkey/rkey, and AVL node.
- `iser_vmem_mr_pool_t`: HCA-bound vmem pool with MR flags, chunk sizing, total/max size, AVL MR list, and mutex.
- MR quantum/minimum chunk sizes and architecture-dependent chunk/max pool sizes for data and message memory.
- MR flags:
  - Data buffers enable local write, remote read, and remote write.
  - Message buffers enable local write.
- Vmem pool create/destroy/alloc/free/MR lookup prototypes.
- `iser_wr_type_t`: send, RDMA write, RDMA read, or undefined.
- `iser_wr_t`: send completion context referencing an iSER message, IDM buffer, or IDM PDU.
- WR cache constructor/destructor/get/free prototypes.
- `iser_msg_t`: registered control PDU/text message handle with back-pointer cache, SGE, and two MR handles.
- Message cache constructor/destructor/get/free prototypes.
- `iser_buf_t`: data buffer object with cache, buffer, length, MR, SGE, debug copies of WR/WC, and construction/destruction timestamps.
- Buffer cache constructor/destructor and HCA cache init/fini prototypes.
- In-place RDMA memory registration/deregistration routines for existing IDM buffers.

## Integration Notes

This header manages the registered-memory substrate used by iSER transfer code. Per-HCA caches are referenced from `iser_hca_t` in `iser_ib.h`.

## Risks and Gotchas

- Pool sizes differ sharply between 32-bit and 64-bit kernels.
- Registered-memory pools track MR chunks in an AVL tree; alloc/free and MR lookup must stay synchronized with vmem lifetime.
- Work request completion depends on `iser_wr_t` preserving the correct associated object type.
