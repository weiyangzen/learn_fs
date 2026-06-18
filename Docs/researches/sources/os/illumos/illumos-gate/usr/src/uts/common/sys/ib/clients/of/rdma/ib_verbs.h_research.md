# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_verbs.h

This OFED-derived public/kernel compatibility header defines the illumos OpenFabrics verbs-facing model over IBTF. It supplies the basic RDMA/IB types, object structs, enum values, and function prototypes used by kernel OFED clients.

Core definitions:
- RDMA node and transport types, GIDs, device/port attributes, capabilities, port states, rates, AH attributes, events, completions, CQ notification flags, QP/SRQ attributes, QP states, work request opcodes, and access flags.
- Kernel object wrappers for protection domains, completion queues, shared receive queues, queue pairs, IB devices, and IB clients.
- `ib_device_t` bridges OFED client-visible device identity to IBTF HCA handles, GUIDs, local DMA lkey, port count, registration state, client data, and OFS client handles.
- API declarations cover client register/unregister, client data access, device query, PD allocation, QP lifecycle, CQ lifecycle, polling, notification, and IBTF handle extraction.

Risk-sensitive invariants:
- This is ABI/API compatibility glue; enum values and struct layout must remain aligned with OFED consumers.
- `IB_QPT_SMI` and `IB_QPT_GSI` must remain the first two QP types because MAD code uses them as table indexes.
- CQ notification uses the standard missed-event race protocol: positive return from `ib_req_notify_cq()` means consumers must poll again.
