# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm.h

This is the public umbrella header for the iSCSI Data Mover (IDM) layer. It defines public status codes, callback interfaces, request structures, state-machine audit types, and exported APIs for initiator/target connections, services, buffers, tasks, PDUs, key negotiation, and reference counting.

Key definitions:
- `idm_status_t` covers success, generic failure, no resources, reject, I/O, abort, suspend, header/data digest failures, protocol error, and login failure.
- `idm_client_notify_t` generated from `IDM_CLIENT_NOTIFY_LIST()` includes connection accepted, login failure, login readiness, full-feature phase enabled/disabled, lost/destroyed/failed connection, etc.
- `idm_ffp_disable_t`, `idm_abort_type_t`, `idm_task_state_t`, and `kv_status_t`.
- Forward declarations for IDM connection/service/buffer/PDU/task structures.

Callback types:
- Client notification, PDU receive/error, buffer completion, PDU completion, task completion, header build, StatSN update, and keepalive callbacks.
- `idm_conn_ops_t` groups client callbacks per connection.

Request and address structures:
- `idm_sockaddr_t` union for IPv4/IPv6 socket addresses.
- `SIZEOF_SOCKADDR()` helper.
- `idm_conn_req_t` describes initiator connection creation, including domain/type/protocol, binding, destination, LDI identity, callbacks, and boot-connection flag.
- `idm_svc_req_t` describes target service creation.
- `idm_ipaddr_t`, `idm_addr_t`, and variable-sized `idm_addr_list_t`.

State-machine audit:
- `SM_AUDIT_BUF_MAX_REC`, `sm_audit_record_type_t`, `sm_audit_sm_type_t`, `sm_audit_record_t`, `sm_audit_buf_t`.
- Logging globals and macros: `idm_sm_logging`, `idm_conn_logging`, `idm_svc_logging`, `IDM_SM_LOG`, `IDM_CONN_LOG`, `IDM_SVC_LOG`.
- Audit helper declarations.

Included IDM stack:
- Includes iSCSI protocol, connection state machine, transport, internal IDM structures, text negotiation, and socket transport headers.

Public API groups:
- Initiator: create/connect/disconnect/destroy.
- Target services: create/online/offline/destroy/lookup/hold/release/accept/reject.
- Connection metadata setters for target/initiator names and ISID.
- Data transfer: `idm_buf_tx_to_ini`, `idm_buf_rx_from_ini`, completion calls.
- Key negotiation: negotiate, notice, declare.
- Buffers: allocate/free, bind/unbind, find, buffer-pattern set/check.
- Tasks: allocate/start/abort/cleanup/done/free/find/hold/release.
- PDUs: allocate/init/free/complete/transmit.
- Reference counting: init/destroy/reset/hold/release/wait/async wait/is-held.

Relevance:
- Central kernel iSCSI data movement interface, directly relevant to block storage and virtualization/storage networking in subset A.
