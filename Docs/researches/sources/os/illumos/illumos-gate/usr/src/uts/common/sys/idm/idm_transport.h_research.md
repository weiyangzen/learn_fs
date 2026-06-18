# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_transport.h

This header defines the transport abstraction layer used by IDM. It allows socket and iSER transports to register operation vectors for PDU movement, buffer transfer, key negotiation, and connection/service lifecycle.

Key definitions:
- `IDM_TRANSPORT_PATHLEN` and `IDM_TRANSPORT_HEADER_LENGTH`.
- `idm_transport_type_t`: iSER, sockets, number of types, undefined.
- `idm_transport_caps_t` stores transport capability flags.

Operation typedefs:
- PDU transmit, target buffer TX/RX, initiator Data-In/R2T receive, target Data-Out receive.
- Connection resource allocation/free.
- Target/initiator datamover enable, connection termination.
- Task resource cleanup.
- Key negotiation/notice/declaration.
- Capability probe.
- Buffer allocation/setup/teardown/free.
- Target service create/destroy/online/offline.
- Target connection destroy/connect/disconnect.
- Initiator connection create/destroy/connect/disconnect.

Main structures:
- `idm_transport_ops_t` is the full vtable consumed by IDM.
- `idm_transport_t` stores transport type, device path, LDI handle, ops, and caps.
- `idm_transport_attr_t` is used by transport drivers during registration.

API:
- `idm_transport_register`
- `idm_transport_lookup`
- `idm_transport_setup`
- `idm_transport_teardown`

Dependencies:
- Includes `sys/nvpair.h` and `sys/sunldi.h`.

Relevance:
- Abstraction point between common iSCSI data mover code and concrete transport implementations, including TCP sockets and iSER/RDMA.
