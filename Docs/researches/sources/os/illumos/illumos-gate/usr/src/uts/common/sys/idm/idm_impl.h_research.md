# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_impl.h

This header defines private IDM implementation structures and internal routines. It is the concrete layout contract for services, connections, tasks, buffers, PDUs, ID pools, global state, and internal protocol forwarding.

Key definitions:
- Connection flags: `CF_LOGIN_READY`, `CF_INITIAL_LOGIN`, `CF_ERROR`.
- `idm_conn_type_t`: initiator or target.
- Watchdog and idle timeout constants: `IDM_WD_INTERVAL`, `IDM_TRANSPORT_KEEPALIVE_IDLE_TIMEOUT`, `IDM_TRANSPORT_FAIL_IDLE_TIMEOUT`.

Reference counting:
- Audit records and circular audit buffer: `refcnt_audit_record_t`, `refcnt_audit_buf_t`.
- `REFCNT_AUDIT()` captures stack traces with `getpcstack`.
- `idm_refcnt_t` tracks refcount, referenced object, wait mode, mutex/CV, callback, and audit buffer.

Core structures:
- `idm_conn_param_t` stores negotiated connection parameters.
- `idm_svc_t` stores target service state, refcounting, online flag, socket/iSER service-private pointers, and service request.
- `idm_conn_t` stores connection identity, local/remote addresses, target/initiator names, TSIH/ISID strings, connection state/audit/timeout/taskq, login and datamover state, transport ops/type/private data, params, and callbacks.
- `idm_task_t` stores task binding, mutex, client private data/handle, tags, state/refcount, transfer statistics, expected DataSN/R2TSN, input/output buffers, transport header, and phase-collapse flags.
- `idm_buf_t` stores buffer magic, TX/list links, connection binding, buffer pointer/length/offset, expected offset, transport private data, completion callback, task binding, timestamps, socket-specific state, template data header, and status.
- `idm_pdu_t` stores PDU magic, TX/client links, connection, header/data pointers and lengths, transport header/private data, callback, status, iovec receive support, allocation/cache flags, and taskq entry.
- `idm_tx_obj_t` is a generic TX-list discriminator whose first fields match PDU/buffer ordering requirements.
- `idm_idpool_t` is a compact connection-ID pool.
- `idm_global_t` stores global taskqs, watchdog thread, service/connection lists, caches, task ID table, connection ID pool, and socket PDU/buffer caches.

Constants and macros:
- `IDM_CONN_HEADER_DIGEST`, `IDM_CONN_DATA_DIGEST`, `IDM_CONN_USE_SCOREBOARD`.
- `IDM_CONN_ISINI`, `IDM_CONN_ISTGT`.
- Task/buffer/PDU magic values and flags.
- `PDU_MAX_IOVLEN`, `IDM_PDU_OPCODE`.
- AHS cache constants for extended CDB and bidirectional AHS.
- ID pool min/max sizing.

Internal functions:
- Task constructor/destructor.
- ID pool create/destroy/alloc/free.
- PDU RX/TX forwarding and protocol-error paths.
- Login/logout parser helpers.
- Service connection create/destroy; initiator/target finish.
- Common connection create/destroy/close.
- Connection ID allocation/free.
- CRC32C helpers.
- Buffer list insertion and connection lookup by ISID/TSIH/CID.

Dependencies:
- Includes AVL, socket internals, and taskq internals.
- Depends on iSCSI protocol types via inclusion order from `idm.h`.

Relevance:
- Core private kernel data mover state for iSCSI block storage. This is one of the most important files in this group for storage-path behavior.
