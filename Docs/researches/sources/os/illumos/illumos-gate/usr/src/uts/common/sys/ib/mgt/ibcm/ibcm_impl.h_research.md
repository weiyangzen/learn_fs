# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_impl.h

## Scope

Private implementation header for the InfiniBand Connection Manager (IBCM). It defines CM state machines, connection and SIDR state records, service registration records, per-HCA/port/QP registries, CM MAD wire structures, timeout/list helpers, global state, and internal function prototypes.

## State Machines And Constants

- `ibcm_conn_state_t` models RC connection establishment, failure, established, teardown, UD SIDR, and delete states.
- `ibcm_ap_state_t` models LAP/APR alternate-path state.
- `ibcm_event_type_t` maps incoming and outgoing CM protocol messages, including stale lookup cases, to internal event values.
- CM attribute IDs are derived from `IBCM_ATTR_BASE_ID` plus the first 11 event values.
- Defines retry, ID allocation, RNR retry, MAD size, MAD header size, and maximum ComID/ReqID/service ID ranges.
- `ibcm_mode_t` distinguishes active and passive CM sides.
- `ibcm_status_t` communicates lookup results, response actions such as send REJ/REP/RTU/APR/SIDR_REP, defer, success, and failure.

## Core Data Structures

- `ibcm_mad_addr_t` records IBMF local/global addressing for received or outgoing CM MADs, including GRH presence, IBMF handle, port number, and CM QP entry.
- `ibcm_state_data_t` is the main RC connection state object. It stores AVL links, local/remote IDs and QPNs, mode/state/AP state, channel, refcount, service ID, client handler, HCA pointer, stored MADs, timeout data, retry counters, QP/path attributes, flow flags, client private data, service info, condition variables, API return pointers, queued open/close links, trace data, request message pointer, and RNR retry count.
- `ibcm_ud_state_data_t` tracks UD SIDR state: request ID, service ID, handler, HCA, stored reply, timeout/retry data, request source address, server-provided QPN/Q_Key, client private data, condition variables, and return data.
- `ibcm_svc_info_t` and `ibcm_svc_bind_t` represent service ID registrations and their bound GID/P_Key/port/service data/name records.
- `ibcm_ar_t` tracks alternate route or address-resolution style service-record state, waiters, rewrite state, owning IBT handles, SA handle, and HCA.
- `ibcm_qp_list_t`, `ibcm_port_info_t`, and `ibcm_hca_info_t` model per-P_Key CM QPs, per-port IBMF/SAA handles, and per-HCA CM state including AVL trees, SIDR list, ID arenas, counters, and port array.

## Wire Formats

Defines on-wire CM message payload structures:

- `ibcm_req_msg_t` for REQ, including service ID, local CA GUID/Q_Key/QPN/EECN, responder/initiator resources, timeout/retry fields, P_Key, MTU/RNR/SRQ bits, primary and alternate path data, and private data.
- `ibcm_mra_msg_t`, `ibcm_rej_msg_t`, `ibcm_rep_msg_t`, `ibcm_rtu_msg_t`, `ibcm_dreq_msg_t`, `ibcm_drep_msg_t`.
- `ibcm_lap_msg_t` and `ibcm_apr_msg_t` for alternate path migration.
- `ibcm_sidr_req_msg_t` and `ibcm_sidr_rep_msg_t` for UD service-ID resolution.
- `ibcm_classportinfo_msg_t` for CM ClassPortInfo response data.
- `ibcm_ip_pvtdata_t` for RDMA CM IP private data, with endian-specific bitfields and IPv4 aliases into IPv6 addresses.

## Internal APIs

- IBMF receive callback: `ibcm_recv_cb()`.
- Per-message state handlers: `ibcm_process_req_msg()`, `rep`, `rtu`, `dreq`, `drep`, `rej`, `mra`, `apr`, `lap`, `sidr_req`, and `sidr_rep`.
- CEP/QP transition helpers process REQ/REP/RTU/REJ/LAP/APR/DREQ and client callback results.
- MAD posting helpers build reply addresses and post/resend REJ, REP, RTU, DREQ, DREP, LAP, APR, MRA, SIDR_REQ, and SIDR_REP messages through IBMF.
- Lookup/lifetime helpers manage RC state AVL entries, SIDR list entries, service entries, ComIDs, ReqIDs, local/IP service IDs, transaction IDs, HCA references/resources/services, and timeout-list processing.
- SA and path helpers include SA access throttling/contact, node info lookup, path cache init/fini/purge, service-data swizzling, AR init/fini, and IP debug printing.

## Synchronization

- `state_mutex` protects RC state, refcounts, timers, retry counters, callback proceed flags, and MRA/abort fields.
- `ud_state_mutex` protects SIDR state, refcount, timer, retry, send flags, and blocking state.
- HCA AVL trees are protected by `hca_state_rwlock`; SIDR lists by `hca_sidr_list_lock`.
- Service rewrite and unbind paths coordinate through `ibcm_svc_info_lock` and `ibcm_svc_info_cv`.
- Global locks cover HCA list/counters, QP list, multicast group list, receive path, and timeout list.
- Lock order annotations document state-lock to timeout-list ordering and HCA-tree/SIDR-list locks before state locks.

## Dependencies

- Relies on IBTL private CM interfaces, IBMF, IBMF SAA, kernel AVL/vmem/taskq/timeout primitives, IP definitions, and CM public data from IBT.
- Stores IBMF messages directly and reuses IBMF callbacks for asynchronous send completion and receive dispatch.
- Uses SA records for service registration rewrite and path/service lookup behavior.

## Risks And Invariants

- State object lifetime depends on refcounts plus delayed timeout-list deletion; `delete_state_data` and `ud_delete_state_data` defer freeing until references drain.
- Timers store expected CM/AP states to validate callbacks against current state before retransmitting or failing a connection.
- AVL lookup keys differ by active/passive path and message type; incorrect tree choice can misidentify duplicate, stale, or valid messages.
- Stored MADs and send flags must remain synchronized with IBMF completions and timeout retransmits.
- Service record rewrite state must prevent unbind from freeing records while SA rewrite is in progress.
- CM MAD structures are wire contracts; packed bit fields and byte-array GIDs/SIDs exist to handle non-aligned protocol fields.
