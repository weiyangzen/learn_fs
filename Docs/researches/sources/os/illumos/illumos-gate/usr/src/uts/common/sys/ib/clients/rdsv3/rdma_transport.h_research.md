# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdma_transport.h

This small RDSv3 RDMA transport header declares RDMA transport initialization and RDMA-CM integration.

Core definitions:
- `RDSV3_RDMA_RESOLVE_TIMEOUT_MS` is 5000 ms.
- `rdsv3_rdma_cm_event_handler()` is the RDMA-CM event callback.
- `rdsv3_rdma_init()` and `rdsv3_rdma_exit()` manage RDMA transport layer state.
- IB transport init/exit and `rdsv3_ib_transport` are declared.

Risk-sensitive invariants:
- RDMA-CM route/address resolution timeout is part of connection behavior.
- RDMA transport lifecycle must coordinate with IB transport registration and shutdown.
