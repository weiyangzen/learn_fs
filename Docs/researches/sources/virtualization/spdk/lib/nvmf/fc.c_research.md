# File Research: sources/virtualization/spdk/lib/nvmf/fc.c

Read completely: yes, 4007 lines.

Purpose: implements the NVMe-oF Fibre Channel transport integration, including transport registration, FC hardware port/nport/rport administration, poll-group and hardware-queue routing, IO request lifecycle, ABTS handling, and SPDK transport callbacks.

Major components:
- FC tracepoint registration and request state naming.
- Global FC transport state: `g_nvmf_ftransport`, `g_spdk_nvmf_fc_port_list`, `g_nvmf_fc_main_thread`, and FC poll groups.
- Per-connection request pools sized at twice queue depth to tolerate CQ/RQ race windows.
- HWQP initialization with DPDK hash tables for connection IDs and RPIs.
- Poll-group assignment, add/remove HWQP messaging, and FC queue polling.
- FC admin event handlers for HW port init/free/online/offline/reset, nport create/delete, I_T add/delete, and ABTS receive.

IO path:
- `nvmf_fc_hwqp_process_frame()` dispatches LS requests to `fc_ls.c` or command IUs to `nvmf_fc_hwqp_handle_request()`.
- `nvmf_fc_hwqp_handle_request()` validates command IU fields, rejects bidirectional transfers, looks up connection ID, validates source/destination IDs, checks association/connection/qpair state, enforces max IO size, allocates an FC request, copies NVMe command data, records VMID/priority, and executes or queues pending-buffer work.
- `nvmf_fc_request_execute()` allocates exchange and data buffers, then either receives host-to-controller data or submits read/no-data commands to the generic NVMf executor.
- `nvmf_fc_request_complete()` sends read data, ERSP/RSP responses, or abort completion depending on request state and completion status.

Abort and ABTS handling:
- `nvmf_fc_handle_abts_frame()` identifies HWQPs with active connections for an RPI, sends ABTS work to pollers, and emits BLS accept/reject.
- If no OXID is found and queue sync is available, the code posts queue-sync markers and retries.
- `nvmf_fc_request_abort()` marks requests aborted, notifies bdev for bdev-phase work, issues FC aborts for transfer/response phases, removes pending/fused requests directly, and completes through poller API.

Transport API:
- Registers `spdk_nvmf_transport_fc`.
- Defaults: max queue depth 128, admin depth 32, max qpairs per controller 5, max IO size 65536, IO unit size 4096.
- `nvmf_fc_create()` requires at least two cores, initializes the low-level driver, registers an accept poller, and records the main thread.
- `nvmf_fc_discover()` fills FC discovery log fields.
- Listen/stop-listen are stubs returning success/no-op; actual FC nport listener population is handled by admin nport events.

Administration model:
- Low-level FC driver events are funneled through `nvmf_fc_main_enqueue_event()` onto the FC main thread.
- HW port online marks LS and IO queues online and assigns IO queues to least-loaded FC poll groups.
- HW port offline marks queues offline and asynchronously removes HWQPs from poll groups.
- Nport creation also adds FC listener addresses to subsystems allowing any listener.
- Nport deletion removes listener addresses and deletes all rports.
- I_T delete removes pending LS work, marks rport deleting, deletes all matching associations, and frees rport after associations drain.

Concurrency and ownership:
- Main-thread assertions protect FC admin object mutation.
- Poll-group list updates are protected by `g_nvmf_ftransport->lock`.
- Many operations are asynchronous through `spdk_thread_send_msg()` and callback contexts.
- Request objects are pool-owned by connections; `_nvmf_fc_request_free()` returns exchange, buffers, and request object.

Notable risks and sharp edges:
- `nvmf_fc_adm_evnt_hw_port_offline()` initializes `pending_remove_hwqp` to `num_io_queues`; a zero-IO-queue port would not use the async callback path.
- Several admin paths use `DEV_VERIFY()` for conditions that become non-fatal in promoted builds, so callers may see partial zombie states.
- `nvmf_fc_adm_add_rem_nport_listener()` calls `spdk_nvmf_tgt_listen_ext()` even on remove path before pausing/removing listener, which is unusual but matches current code.
- The code relies heavily on correct callback ownership; duplicate delete operations often return `-ENODEV` rather than queueing callbacks.

Dependencies:
- Works with `fc_ls.c` for LS association/connection handling.
- Delegates hardware operations to `fc_lld.h` functions.
- Uses generic NVMf transport hooks, qpair lifecycle, request execution, and subsystem listener APIs.
