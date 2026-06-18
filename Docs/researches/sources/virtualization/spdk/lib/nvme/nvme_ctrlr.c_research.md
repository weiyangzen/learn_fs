# File Research: sources/virtualization/spdk/lib/nvme/nvme_ctrlr.c

## Purpose

`nvme_ctrlr.c` is the core SPDK NVMe controller lifecycle implementation. It manages controller options, admin and I/O queue pairs, initialization/reset/destruction state machines, namespace discovery, asynchronous event handling, multi-process ownership, keep-alive, controller memory regions, namespace management commands, firmware/boot partition operations, and controller metadata accessors.

It is the main controller orchestration layer between public `spdk_nvme_ctrlr_*` APIs and transport-specific operations.

## Main Responsibilities

- Controller option defaults and ABI-compatible option copying.
- I/O qpair allocation, connect, disconnect, reconnect, and free.
- Controller register access wrappers for CAP, VS, CC, CSTS, CMB, PMR, boot partition registers, and NSSR.
- Controller initialization state machine through `nvme_ctrlr_process_init()`.
- Controller reset/disconnect/reconnect flows.
- Controller destruction and shutdown notification.
- Identify Controller, Identify Namespace, Active Namespace List, Namespace ID Descriptor List, and I/O command set specific identify flows.
- Supported log page and feature discovery.
- Asynchronous Event Request setup and event dispatch.
- ANA log allocation, retrieval, parsing, and namespace ANA state updates.
- Per-process controller tracking for SPDK multi-process operation.
- Public controller APIs for namespace attach/detach/create/delete/format, firmware update, CMB/PMR, boot partitions, security send/receive, and authentication.

## Controller Initialization State Machine

The central initialization function is `nvme_ctrlr_process_init()`. It advances `ctrlr->state` through transport setup and NVMe controller bring-up. Major phases are:

1. Optional PCIe init delay.
2. Connect admin qpair.
3. Read version register `VS`.
4. Read capability register `CAP`.
5. Read controller configuration `CC` and determine whether disabling is required.
6. If enabled, wait for `CSTS.RDY`, clear `CC.EN`, and wait for disabled.
7. Enable controller:
   - Select page size.
   - Select command set.
   - Validate arbitration mechanism.
   - Program `CC.EN = 1`.
8. Wait for `CSTS.RDY = 1`.
9. Reset admin queue transport state.
10. Identify Controller.
11. Configure Asynchronous Event Requests.
12. Configure keep-alive.
13. Identify NVM/ZNS/KV I/O command set specific controller data.
14. Set number of I/O queues.
15. Discover active namespaces.
16. Identify namespaces.
17. Identify namespace descriptor lists.
18. Identify namespace I/O command set specific data.
19. Discover supported log pages and features.
20. Set Host Behavior Support feature if needed.
21. Configure doorbell buffer if supported.
22. Set Host ID if needed.
23. Run transport ready hook.
24. Enter `NVME_CTRLR_STATE_READY`.

The state machine uses async register operations and async admin commands, then polls admin completions from wait states. It tracks per-state timeouts using SPDK ticks and avoids recursive admin completion processing when already in admin completion context.

## Controller Options

`spdk_nvme_ctrlr_get_default_ctrlr_opts()` populates defaults with ABI-size checks:

- I/O queue count, size, and request count.
- CMB submission queue preference.
- Interrupt enablement.
- Arbitration configuration.
- Keep-alive timeout.
- Transport retry and ACK timeout settings.
- Host NQN and host identifiers.
- Command set selection.
- Admin timeout and admin queue size.
- NVMe/TCP header/data digest settings.
- Fabrics connect timeout.
- ANA and changed namespace log read controls.
- TLS PSK and DH-HMAC-CHAP keys/digest/group allow-lists.

The default host NQN and extended host ID come from the global driver object initialized in `nvme.c`.

## I/O Qpair Lifecycle

Key public APIs:

- `spdk_nvme_ctrlr_get_default_io_qpair_opts()`
- `spdk_nvme_ctrlr_alloc_io_qpair()`
- `spdk_nvme_ctrlr_connect_io_qpair()`
- `spdk_nvme_ctrlr_disconnect_io_qpair()`
- `spdk_nvme_ctrlr_reconnect_io_qpair()`
- `spdk_nvme_ctrlr_free_io_qpair()`

Qpair allocation validates:

- Controller is ready.
- Queue priority is compatible with selected arbitration.
- User-provided SQ/CQ buffers are large enough.
- Delayed command submission is not used with interrupts.

The controller maintains:

- `active_io_qpairs`
- Per-process `allocated_io_qpairs`
- `free_io_qids` bit array

Freeing a qpair handles completion-context deletion deferral, disconnect polling for async qpairs, poll group removal, queued request aborting for local qpairs, qid release, and transport deletion.

## Reset, Disconnect, and Failure Handling

- `nvme_ctrlr_fail()` marks the controller failed, optionally removed, sets error state, and disconnects adminq.
- `spdk_nvme_ctrlr_fail()` wraps it with controller locking.
- `nvme_ctrlr_disconnect()` starts reset/disconnect:
  - Marks resetting/disconnecting.
  - Disables keep-alive.
  - Aborts queued aborts and AERs.
  - Marks adminq local failure.
  - Disconnects adminq.
- `spdk_nvme_ctrlr_reset()` performs synchronous reset by disconnecting, processing admin completions until disconnect, reconnecting, and polling reinitialization.
- `spdk_nvme_ctrlr_reconnect_async()` sets state back to init and intentionally leaves the controller lock held until `spdk_nvme_ctrlr_reconnect_poll_async()` completes.
- `spdk_nvme_ctrlr_reconnect_poll_async()` reinitializes the controller, reconnects non-fabrics qpairs where possible, marks foreign qpairs for owner-process reset handling, removes inactive namespaces, and emits controller update messages if needed.

Subsystem reset is exposed through `spdk_nvme_ctrlr_reset_subsystem()` and writes NSSR only when supported.

## Identify and Namespace Discovery

Namespace objects are stored in an RB tree ordered by NSID.

Active namespace discovery uses `nvme_active_ns_ctx`:

- For old/quirked controllers, it synthesizes all namespaces from `1..NN`.
- Otherwise it issues one or more Active Namespace List identify commands.
- It handles multi-page namespace lists by reallocating the list buffer and continuing from the last returned NSID.
- It swaps controller namespace state by clearing removed namespaces and marking new/existing namespaces as pending identify.

Namespace identify flow:

- `nvme_ctrlr_identify_namespaces()` identifies all pending namespaces.
- `nvme_ctrlr_identify_id_desc_namespaces()` retrieves namespace ID descriptor lists when supported.
- `nvme_ctrlr_identify_namespaces_iocs_specific()` retrieves ZNS, KV, or NVM-specific namespace data when supported.

The code treats some namespace identify failures as non-fatal when they indicate namespaces became inactive during discovery.

## Command Set Specific Handling

Controller-level I/O command set data:

- `nvme_ctrlr_identify_iocs_nvm_specific()`
- `nvme_ctrlr_identify_iocs_zns_specific()`
- `nvme_ctrlr_identify_iocs_kv_specific()`

ZNS-specific behavior includes:

- Reading ZNS controller identify data.
- Computing `max_zone_append_size`.
- Reading the ZNS Command Effects log page.
- Setting `SPDK_NVME_CTRLR_ZONE_APPEND_SUPPORTED` when Zone Append is supported.

The controller command set is selected during enable based on CAP.CSS and caller options, with fallbacks for buggy targets.

## Log Pages, Features, ANA, and AERs

Supported log pages:

- Mandatory log pages are marked directly.
- Command Effects Log is marked if controller LPA says CSES.
- ANA log is marked when CMIC indicates ANA reporting.
- FDP logs are marked when FDP is advertised.
- Intel vendor log pages are discovered through Intel log page directory for PCIe Intel devices unless disabled by quirks.

ANA handling:

- `nvme_ctrlr_alloc_ana_log_page()` sizes buffers based on active namespace count and ANA group count.
- `nvme_ctrlr_update_ana_log_page()` fetches the ANA log page synchronously through the admin queue.
- `nvme_ctrlr_parse_ana_log_page()` copies each variable-sized descriptor before passing it to a callback.
- `nvme_ctrlr_update_ns_ana_states()` updates namespace ANA group/state.

AER handling:

- `nvme_ctrlr_configure_aer()` configures requested async event notices.
- `nvme_ctrlr_construct_and_submit_aer()` submits AER commands.
- `nvme_ctrlr_async_event_cb()` queues events to every active process and resubmits AERs unless removed/destructed.
- `nvme_ctrlr_process_async_event()` handles namespace attribute changes and ANA changes.
- Namespace change processing can use Changed Namespace List log or fall back to full active namespace rediscovery.

## Multi-Process Tracking

The controller maintains `active_procs`, each with:

- PID and primary/secondary flag.
- Active request queue.
- Per-process allocated I/O qpairs.
- Async event queue.
- Timeout callbacks and AER callbacks.
- Process-local PCI device handle.

Important functions:

- `nvme_ctrlr_add_process()`
- `nvme_ctrlr_remove_process()`
- `nvme_ctrlr_cleanup_process()`
- `nvme_ctrlr_remove_inactive_proc()`
- `nvme_ctrlr_proc_get_ref()`
- `nvme_ctrlr_proc_put_ref()`
- `nvme_ctrlr_get_ref_count()`

Inactive process cleanup uses `kill(pid, 0)` and `ESRCH` detection, then frees outstanding requests, async events, and qpairs owned by the dead process.

## Destruction and Shutdown

`nvme_ctrlr_destruct_async()` prepares destruction by:

- Marking controller destructed.
- Processing admin completions.
- Aborting queued aborts and AERs.
- Freeing active I/O qpairs.
- Freeing doorbell and command-set-specific data.
- Starting shutdown notification through `nvme_ctrlr_shutdown_async()`.

`nvme_ctrlr_shutdown_async()` reads CC, sets shutdown notification or disables the controller depending on options, and then `nvme_ctrlr_shutdown_poll_async()` polls CSTS.SHST until complete or timeout.

`nvme_ctrlr_destruct_poll_async()` completes shutdown, invokes detach callback, disconnects adminq, clears namespaces, frees qid bit arrays, ANA buffers, and calls transport destruct.

## Public Controller Utility APIs

The file exposes many controller metadata and operation APIs, including:

- Controller data/register access:
  - `spdk_nvme_ctrlr_get_data()`
  - `spdk_nvme_nvm_ctrlr_get_data()`
  - `spdk_nvme_ctrlr_get_regs_*()`
  - `spdk_nvme_ctrlr_get_num_ns()`
  - `spdk_nvme_ctrlr_get_ns()`
  - `spdk_nvme_ctrlr_get_pci_device()`
  - `spdk_nvme_ctrlr_get_numa_id()`
  - `spdk_nvme_ctrlr_get_id()`
  - `spdk_nvme_ctrlr_get_max_xfer_size()`
  - `spdk_nvme_ctrlr_get_max_sges()`
  - `spdk_nvme_ctrlr_get_flags()`
  - `spdk_nvme_ctrlr_get_transport_id()`

- Namespace management:
  - `spdk_nvme_ctrlr_attach_ns()`
  - `spdk_nvme_ctrlr_detach_ns()`
  - `spdk_nvme_ctrlr_create_ns()`
  - `spdk_nvme_ctrlr_delete_ns()`
  - `spdk_nvme_ctrlr_format()`

- Firmware and boot partitions:
  - `spdk_nvme_ctrlr_update_firmware()`
  - `spdk_nvme_ctrlr_read_boot_partition_start()`
  - `spdk_nvme_ctrlr_read_boot_partition_poll()`
  - `spdk_nvme_ctrlr_write_boot_partition()`

- Controller memory:
  - `spdk_nvme_ctrlr_reserve_cmb()`
  - `spdk_nvme_ctrlr_map_cmb()`
  - `spdk_nvme_ctrlr_unmap_cmb()`
  - `spdk_nvme_ctrlr_enable_pmr()`
  - `spdk_nvme_ctrlr_disable_pmr()`
  - `spdk_nvme_ctrlr_map_pmr()`
  - `spdk_nvme_ctrlr_unmap_pmr()`

- Security/auth:
  - `spdk_nvme_ctrlr_security_receive()`
  - `spdk_nvme_ctrlr_security_send()`
  - `spdk_nvme_ctrlr_authenticate()`
  - `spdk_nvme_ctrlr_set_keys()`

## Important Dependencies

- `nvme_internal.h` for controller, namespace, qpair, state, and request internals.
- `nvme_io_msg.h` for controller update messaging.
- Transport dispatch functions for qpair/controller construction, connect/disconnect, register access, CMB/PMR, memory domains, and readiness.
- Admin command constructors from companion command files.
- SPDK environment APIs for DMA/shared allocation, virtual-to-physical translation, ticks, delays, PCI handling, and bit arrays.

## Error Handling and Risks

- The initialization state machine is broad and timeout-driven; incorrect timeout or state transition behavior can stall probe/reset.
- Several operations deliberately treat optional feature failures as non-fatal, such as Host ID setting and Intel log page discovery.
- Namespace discovery handles active namespace changes but may clear namespace state when identify returns inactive/invalid errors.
- Multi-process cleanup assumes process liveness can be detected with `kill(pid, 0)`.
- Some reset/reconnect paths intentionally hold controller locks across async-style phases; callers must respect API contract.
- Boot partition write uses controller fields as operation state, so concurrent boot partition writes on one controller would conflict.
- Debug/error handling often logs and continues for optional device features, reflecting real-world controller quirks.

## Filesystem/Virtualization Relevance

This file is central to SPDK’s user-space NVMe controller model. It supplies the controller lifecycle and namespace surface that higher-level block devices, NVMe-oF initiators, virtualized storage backends, and filesystem-adjacent storage tooling rely on for discovery, queue setup, reset recovery, namespace changes, and secure/admin operations.
