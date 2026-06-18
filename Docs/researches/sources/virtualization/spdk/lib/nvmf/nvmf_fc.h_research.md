# File Research: sources/virtualization/spdk/lib/nvmf/nvmf_fc.h

## Purpose

`nvmf_fc.h` is the private Fibre Channel transport header for SPDK NVMe-oF. It defines the FC transport's internal object model, request state machine, low-level driver event interface, poller API, and helper prototypes used by FC implementation files. It sits below the public `spdk/nvmf.h` API and above low-level FC target driver callbacks.

## Main Structures And APIs

- Defines FC limits and handles: `SPDK_NVMF_FC_TR_ADDR_LEN`, `NVMF_FC_INVALID_CONN_ID`, `SPDK_MAX_NUM_OF_FC_PORTS`, opaque `spdk_nvmf_fc_lld_hwqp_t`, and `spdk_nvmf_fc_lld_fc_port_t`.
- Models FC object and queue state through `spdk_fc_port_state`, `spdk_fc_hwqp_state`, `spdk_nvmf_fc_object_state`, and `spdk_nvmf_fc_request_state`.
- `spdk_nvmf_fc_port` represents a hardware FC port, including LS queue, IO queues, nport list, IO resource pool, and vendor context.
- `spdk_nvmf_fc_hwqp` represents a hardware queue pair/poller context, with FC port linkage, thread, hash tables for connections and remote ports, in-use requests, pending LS queue, sync callbacks, counters, and vendor context.
- `spdk_nvmf_fc_poll_group` wraps `spdk_nvmf_transport_poll_group` and owns the FC HWQPs assigned to an SPDK poll group.
- `spdk_nvmf_fc_nport`, `spdk_nvmf_fc_remote_port_info`, `spdk_nvmf_fc_association`, and `spdk_nvmf_fc_conn` model target N_Port, initiator remote port, FC-NVMe association, and transport connection. `spdk_nvmf_fc_conn` embeds `spdk_nvmf_qpair` as its first field and tracks queue depth, fused commands, request pools, state, and delete/fini callbacks.
- `spdk_nvmf_fc_request` embeds `spdk_nvmf_request` as its first field and adds FC-specific exchange, OXID/RPI, request state, transfer length, abort callback list, command IU, ERSP IU, and tracing fields.
- `spdk_nvmf_fc_ls_rqst` and `spdk_nvmf_fc_rq_buf_ls_request` define Link Service request/response storage and enforce exact LS receive buffer sizing with `SPDK_STATIC_ASSERT`.
- `spdk_nvmf_fc_errors` collects per-HWQP transport counters for exchange exhaustion, invalid ports, frame errors, queue errors, buffer allocation, aborts, read/write failures, and connection/rport issues.
- Poller API types cover add/delete connection, quiesce/activate queue, ABTS received, request abort completion, adapter events, AENs, queue sync, and HWQP add/remove.
- FC driver event types in `spdk_fc_event` cover hardware port lifecycle, nport create/delete, I_T add/delete, ABTS, port dump/reset, unrecoverable error, and port free.

## Control Flow And Integration

The header defines two async-facing control planes. The first is the SPDK poller API: callers pass typed argument structs to `nvmf_fc_poller_api_func()` to mutate queue-local connection and request state on the correct thread. The second is the low-level FC driver event path: the driver submits `spdk_fc_event` payloads through `nvmf_fc_main_enqueue_event()` and receives completion via `spdk_nvmf_fc_callback`.

The FC request path is represented by `spdk_nvmf_fc_request_state`: commands move from initialization through read/write buffer, FC transfer, bdev execution, response, success/failure/abort, and fused-waiting states. `nvmf_fc_req_in_xfer()` identifies states already in FC transfer/response handling, while `nvmf_fc_send_ersp_required()` and `nvmf_fc_handle_rsp()` are declared for response completion.

The header also supplies container helpers: `nvmf_fc_get_fc_req()` converts generic `spdk_nvmf_request` to FC request, and `nvmf_fc_get_conn()` converts generic qpair to FC connection. Static asserts require the embedded generic objects to remain at offset zero.

## Dependencies

This file depends on SPDK NVMe/NVMe-oF public headers, FC-NVMe spec definitions, SPDK threading, `nvmf_internal.h`, queue macros, and DPDK `rte_hash`. It is tightly coupled to the private core target model through embedded `spdk_nvmf_qpair`, `spdk_nvmf_request`, `spdk_nvmf_tgt`, `spdk_nvmf_subsystem`, and transport poll group objects.

## Risks And Edge Cases

The highest-risk areas are asynchronous lifecycle and abort handling: associations, connections, HWQPs, and requests can be deleted while callbacks, ABTS handling, queue syncs, or backend aborts are outstanding. Request pool ownership is per connection, so stale request links or missed frees can corrupt transport state. FC IDs, RPIs, OXIDs, and exchange IDs are stored in compact integer fields and must stay valid across driver callbacks. `nvmf_fc_dump_buf_print()` bounds output to `SPDK_FC_HW_DUMP_BUF_SIZE`, but callers must provide valid dump buffers and offsets.

## Test/Validation Signals

Useful validation should cover LS create/delete association and connection flows, port online/offline/quiesce transitions, HWQP add/remove, request state transitions for read/write/no-data commands, fused command waiting, ABTS receive and request abort completion, queue sync callbacks, and failure paths for invalid RPI/OXID/connection IDs.
