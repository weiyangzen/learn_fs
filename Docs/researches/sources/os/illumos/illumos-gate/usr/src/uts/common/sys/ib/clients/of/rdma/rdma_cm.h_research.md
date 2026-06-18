# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/rdma_cm.h

This OFED-derived header declares the kernel RDMA Connection Manager API exposed to OpenFabrics-style clients on illumos.

Core definitions:
- CM event types for address/route resolution, connection requests/responses, rejects, establishment, disconnect, device removal, multicast, and address change.
- RDMA port spaces for SDP, IPoIB, TCP, UDP, and SCTP.
- `rdma_addr`, `rdma_route`, connected and UD connection parameter structs, and `rdma_cm_event`.
- `rdma_cm_id`, which binds a device, caller context, optional QP, event handler, route, port space, and port number.

API surface:
- ID creation/destruction, address binding/resolution, route resolution, QP attribute initialization, active connect, listen, accept, reject, disconnect, event notification, multicast join/leave, service type selection, and RDMA-CM-owned QP create/destroy.
- illumos-specific mapping helpers attach IBTF/iWARP client handles and QP handles to an RDMA-CM ID.

Important semantics:
- Destroying an ID cancels in-flight async operations.
- Event callbacks must not directly call `rdma_destroy_id()` on the same ID; returning nonzero requests destruction.
- RDMA-CM-owned QPs are automatically transitioned by CMA.
