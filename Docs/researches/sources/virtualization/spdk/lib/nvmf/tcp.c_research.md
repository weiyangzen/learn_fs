# File Research: sources/virtualization/spdk/lib/nvmf/tcp.c

SPDK NVMe-oF TCP transport implementation. This is the concrete transport backend registered as `"TCP"` for the generic NVMf transport layer.

Key responsibilities:
- Defines TCP transport defaults, transport-specific JSON options, and the `spdk_nvmf_transport_tcp` ops table.
- Implements TCP transport creation/destruction, listener setup/teardown, accept polling, discovery-log population, and poll-group management.
- Maintains per-qpair request, PDU, socket, trace, in-capsule buffer, and state-machine resources.
- Implements the NVMe/TCP connection handshake via ICReq/ICResp, including header/data digest negotiation and receive-buffer sizing.
- Parses incoming PDU common headers, PDU-specific headers, payloads, data digests, and error/termination requests.
- Drives the main TCP request state machine from capsule command receipt through buffer acquisition, optional zero-copy, R2T/H2C transfer, target execution, C2H data/response, and cleanup.
- Handles SGL parsing for transport data blocks and in-capsule data, including the special control-message buffer pool needed when configured ICD is smaller than the NVMe/TCP admin/fabric command maximum.
- Sends R2T, C2H data, capsule response, and C2H termination PDUs, including CPDA padding, optional header/data digests, and accelerated CRC32C when possible.
- Supports DIF insert/strip paths: DIF context detection, host-to-controller DIF generation, controller-to-host DIF verification, and DIF error mapping to NVMe completion status.
- Supports NVMf zero-copy request start/end phases and delayed request release when async writes or zcopy buffers are outstanding.
- Enforces NVMe fused command ordering and failure semantics for FIRST/SECOND command pairs.
- Implements abort handling for TCP requests in executable, buffer-waiting, zcopy, and transfer states.
- Implements experimental TLS support through the `ssl` socket implementation, keyring-backed PSK lookup, PSK identity generation, retained PSK derivation, and host/subsystem PSK add/remove/dump hooks.

Important behavior:
- The request lifecycle is explicit and counter-tracked with `TCP_REQUEST_STATE_*`; state transitions update per-qpair counters and trace points.
- The receive lifecycle is separate from request execution and uses `NVME_TCP_PDU_RECV_STATE_*` to read common headers, PDU-specific headers, request slots, payload buffers, quiescing, and fatal errors.
- Listener `trsvcid` is canonicalized to a numeric TCP port string; invalid or out-of-range service IDs are rejected.
- Secure listeners force the `ssl` socket implementation and mark discovery entries as requiring TLS 1.3.
- A qpair starts in invalid state, becomes initializing while ICResp is being sent, and becomes running only after the ICResp write completes.
- If too many commands arrive but responses or zcopy releases are still pending, capsule command handling can retry instead of immediately terminating.
- If the host exceeds queue depth outside that tolerated window, sends or triggers termination behavior.
- Host-to-controller transfers validate transfer tag, command capsule CID, expected offset, and total length before accepting H2C data.
- In-capsule SGL offset must be zero for NVMe/TCP; unsupported SGL forms are treated as fatal transport errors because payload skipping is not implemented there.
- C2H success optimization can suppress a separate capsule response when C2H data completes successfully with zeroed completion dwords.
- Qpair destruction is deferred through a thread message to avoid freeing qpair state from inside socket callbacks.
- `stop_listen` removes the listening socket from the listen socket group and closes it; higher-level generic code handles listener refcounts and qpair disconnect fanout.
- Interrupt mode registers interrupt objects for both listen socket groups and poll-group socket groups; polling mode uses pollers.
- Socket writes are async and flushed for management/termination PDUs and in interrupt mode.
- PSK material is zeroed before release where local buffers or entries hold secret bytes.

Dependencies:
- Uses SPDK socket APIs (`spdk_sock_*`, sock groups, async writev, flush, socket priorities, TLS impl opts).
- Uses SPDK NVMf core APIs for qpair creation/disconnect, request execution/completion, abort, zcopy, controller options, and transport registration.
- Uses SPDK iobuf through the generic transport layer and TCP control-message pools for special in-capsule cases.
- Uses SPDK accel CRC32C APIs for digest computation/verification fast paths.
- Uses SPDK DIF helpers for metadata generation/verification and NVMe completion mappings.
- Uses SPDK keyring and internal NVMe/TCP helpers for TLS PSK parsing, identity generation, retained PSK derivation, and TLS PSK derivation.
- Uses trace/log infrastructure (`SPDK_TRACE_REGISTER_FN`, trace records, `SPDK_LOG_REGISTER_COMPONENT`).

Notable risks:
- The receive state machine and request state machine are tightly coupled through `tqpair->pdu_in_progress`, request-owned response PDUs, and external completions; invalid transitions can produce leaks, double frees, or stuck qpairs.
- Many fatal error paths send a C2H termination request and then wait for host disconnect; timeout handling is essential to avoid indefinite retention.
- SGL and in-capsule validation is intentionally strict because this code does not implement general payload skipping after malformed command metadata.
- Async socket writes require delayed completion handling when a qpair is disconnected while request PDUs remain in flight.
- Zero-copy paths have extra lifecycle states and special cleanup assertions, especially for failed writes, reads, and inactive qpairs.
- Control-message buffers are shared per poll group; exhaustion queues requests and must be unwound on qpair removal.
- TLS support is explicitly logged as experimental and depends on correct keyring configuration, PSK interchange parsing, and socket implementation behavior.
