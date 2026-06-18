# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser.h

## Purpose

Defines core iSER driver state, operational parameters, iSCSI negotiation keys, service bindings, connection type/stage/state, negotiated operation parameters, connection objects, and top-level iSER public routines.

## Main Definitions

- Includes core DDI, socket, IBT, IDM, and iSER component headers.
- `iser_logging` and `ISER_LOG` conditional logging macro.
- Taskq thread count, iSER header length, and half-second delay constant.
- Operational min/max/implementation/default values for target/initiator receive data segment length and max outstanding unexpected PDUs.
- iSCSI key names relevant to iSER negotiation: RDMA extensions, OF/IF markers, segment lengths, and max outstanding unexpected PDUs.
- `iser_sbind_t`: one service bind handle with GID/GUID.
- `iser_svc_t`: iSER-specific IDM service state with refcount, service ID, server handle, and service-bind list.
- `iser_conn_type_t`: initiator or target connection.
- `iser_conn_stage_t`: staged transition into iSER-assisted mode, including allocation, IDM connected, hello/helloreply send/receive states and failures, logged-in, disconnected, freed, closing, and closed.
- `iser_op_params_t`: negotiated digest, RDMA extension, marker, segment length, and unexpected-PDU parameters.
- `iser_conn_t`: connection lock/stage CV, type, channel, stage, op params, IDM connection, and IDM service.
- `iser_state_t`: driver soft state with devinfo, instance, open refcount, IBT client handle, HCA list, connection list, and global WR cache.
- Status enum and prototypes for IDM registration, service registration/binding/unbinding/deregistration, path lookup, channel allocation/open/close/free, connection destruction, and target service refcount helpers.

## Integration Notes

This is the top-level private iSER header and aggregates the IB, resource, CM, and transfer subheaders. It connects IDM/iSCSI lifecycle to IBT Reliable Connected channels and iSER protocol negotiation.

## Risks and Gotchas

- Connection stages explicitly model failure points during hello exchange; callers should not collapse these states.
- Segment-length defaults reuse iSCSI defaults but iSER imposes larger protocol min/max constraints.
- Service binding is per HCA port through `iser_sbind_t` list entries.
