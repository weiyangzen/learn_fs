# File Research: sources/virtualization/spdk/lib/nvmf/fc_ls.c

Read completely: yes, 1729 lines.

Purpose: implements NVMe/FC Link Service request processing and poller-side FC connection management.

Major responsibilities:
- Formats LS accept/reject headers and reject descriptors.
- Allocates and frees FC associations and their preallocated connection arrays.
- Handles LS Create Association, Create Connection, and Disconnect requests.
- Deletes FC connections and associations asynchronously through poller APIs.
- Maintains poller lookup tables for connection ID and RPI-to-connection lists.
- Exposes `nvmf_fc_poller_api_func()` to marshal poller operations onto HWQP threads.

Association and connection lifecycle:
- `nvmf_fc_ls_new_association()` validates rport presence, initializes host/subsystem NQN data, stores subsystem and transport pointers, allocates connection slots, and links association to nport/rport.
- `nvmf_fc_ls_new_connection()` pulls a connection from the association free list, initializes qpair state, queue depth, RPI, IDs, transport, outstanding queue, and FC trid.
- `nvmf_fc_ls_add_conn_to_poller()` creates per-connection request pools, builds add-connection operation data, and asks generic NVMf target code to place the qpair in a poll group.
- `nvmf_fc_ls_add_conn_cb()` fills returned connection IDs into LS accept responses and transmits them.
- Delete paths mark objects `TO_BE_DELETED`, abort outstanding requests, disconnect qpairs, remove hash entries, return connections to free lists, and free the association when its connection count reaches zero.

LS validation:
- Create Association validates request length, descriptor list length, descriptor tags/lengths, ERSP ratio, admin SQ size, subsystem NQN lookup, and host permission.
- Create Connection validates association ID descriptor, connection command descriptor, ERSP ratio, SQ size, association state, and max qpair count.
- Disconnect validates association ID and disconnect command descriptors before scheduling association deletion.
- Invalid LS commands receive LS reject.

Poller API:
- Add connection inserts connection ID and RPI lookup data.
- Delete connection aborts in-use requests, handles AER specially, disconnects the qpair, removes hash data, and completes callbacks.
- ABTS received searches by RPI/OXID and aborts matching request or reports OXID not found.
- Queue sync stores callback args until a matching sync-done tag arrives.
- Add/remove HWQP updates poll-group HWQP lists on the HWQP thread.

Important data structures:
- Association lists live under nport.
- Rport association counts are incremented/decremented with association membership.
- Connection hash maps `conn_id -> fc_conn`.
- RPI hash maps `rpi -> list of fc_conn` for ABTS lookup.

Concurrency and ownership:
- LS request response buffers are owned by receive queue buffers and released after transmit path.
- Delete callback contexts may be chained on association or connection `ls_del_op_ctx`.
- Poller callbacks are bounced back to the callback thread through `nvmf_fc_poller_api_perform_cb()`.
- Connection deletion waits for qpair finalization when upper-layer disconnect is still pending.

Notable risks and sharp edges:
- `nvmf_fc_ls_alloc_connections()` allocates `(max_qpairs_per_ctrlr + 1) * sizeof(conn)` but loops only `max_qpairs_per_ctrlr`; the extra slot is unused.
- Pointer arithmetic in `nvmf_fc_ls_alloc_connections()` uses `assoc->conns_buf + (i * sizeof(struct spdk_nvmf_fc_conn))`; because `conns_buf` is a `struct spdk_nvmf_fc_conn *`, this scales by struct size twice and appears suspicious unless the declared type differs in headers.
- Delete paths depend on callback completion to free operation contexts and associations; missed callbacks would leak or stall deletion.
- Several reject paths use Create Association request struct aliases for formatting, but only access common header fields.

Dependencies:
- Consumes object types and poller API declarations from `nvmf_fc.h`.
- Uses generic target/subsystem host validation APIs from NVMf core.
- Calls `fc.c` helpers for request pools, connection deletion integration, request abort completion, HWQP validation, and transport/qpair behavior.
