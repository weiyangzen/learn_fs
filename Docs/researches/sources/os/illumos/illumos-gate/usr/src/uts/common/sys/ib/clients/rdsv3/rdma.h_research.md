# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdma.h

This OFED-derived RDSv3 RDMA header defines memory-region and RDMA operation state used by socket options and control messages.

Core definitions:
- `rdsv3_mr` stores AVL linkage, refcount, key, use-once/invalidate/write flags, dead-state bit, owning socket, transport, and transport-private MR data.
- `RDSV3_MR_DEAD` marks a memory region dead using bit operations.
- `rdsv3_rdma_sg` binds a user memory cookie, RDS iovec, send WR, memory-IO handle, and HCA handle.
- `rdsv3_rdma_op` stores remote key/address, write/fence/notify/error/mapped flags, notifier, byte/entry counts, generic scatterlist pointer, and inline RDMA SG array.
- Cookie helpers pack/unpack a 32-bit rkey and 32-bit offset into `rds_rdma_cookie_t`.

API surface:
- Get/free MR socket options, destination-specific MR lookup, key drop, control-message parsing for RDMA args/destination/map, RDMA op free, send complete, and final MR release.

Risk-sensitive invariants:
- MR release is refcounted and finalizes through `__rdsv3_put_mr_final()`.
- Cookie layout is externally visible through RDS RDMA APIs.
- Dead-state bit prevents reuse while outstanding references drain.
