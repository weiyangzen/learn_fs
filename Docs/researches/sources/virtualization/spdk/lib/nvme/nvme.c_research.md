# File Research: sources/virtualization/spdk/lib/nvme/nvme.c

## Purpose

`nvme.c` is the top-level SPDK NVMe library entry point for driver initialization, controller probing/connection, controller detach orchestration, transport-ID parsing/comparison, synchronous admin completion waiting, and common request helpers. It bridges public APIs such as `spdk_nvme_probe()`, `spdk_nvme_connect()`, and `spdk_nvme_detach()` to transport-specific controller construction and controller initialization in `nvme_ctrlr.c`.

## Main Responsibilities

- Owns the global NVMe driver object:
  - `g_spdk_nvme_driver`, stored in an SPDK shared memzone named `spdk_nvme_driver`.
  - `g_spdk_nvme_pid`, process-local PID used for multi-process request ownership.
  - `g_nvme_attached_ctrlrs`, per-process attached controller list.
  - `g_spdk_nvme_driver->shared_attached_ctrlrs`, shared PCIe controller list.

- Initializes shared driver state with `nvme_driver_init()`:
  - Primary process reserves and initializes shared memory.
  - Secondary process waits for primary initialization.
  - Initializes a robust process-shared mutex where supported.
  - Opens PCI hotplug event listener and generates a default extended host ID.

- Handles controller probe/connect:
  - `spdk_nvme_probe()` / `spdk_nvme_probe_ext()` create an async probe context and poll it synchronously.
  - `spdk_nvme_probe_async_ext()` starts a scan without waiting for all controllers to finish initialization.
  - `spdk_nvme_probe_poll_async()` advances controller init and frees the probe context when finished.
  - `spdk_nvme_connect()` / `spdk_nvme_connect_async()` provide direct-connect style construction with caller-supplied controller options.

- Handles detach:
  - `spdk_nvme_detach()` performs blocking detach.
  - `spdk_nvme_detach_async()` appends individual controller detach jobs to a detach context.
  - `spdk_nvme_detach_poll_async()` polls all outstanding detach jobs and frees the detach context when complete.
  - Actual destruction is delegated to `nvme_ctrlr_destruct_async()` / `nvme_ctrlr_destruct_poll_async()`.

- Provides blocking completion helpers:
  - `nvme_completion_poll_cb()` records command completion into `nvme_completion_poll_status`.
  - `nvme_wait_for_completion_poll()` polls a qpair or poll group, checks timeout, checks PCIe CSTS validity, and returns `-EAGAIN`, `0`, `-EIO`, or `-ECANCELED`.
  - `nvme_wait_for_adminq_completion()` wraps admin queue polling with controller admin timeout.

- Provides non-fast-path user-buffer copy request allocation:
  - `nvme_allocate_request_user_copy()` allocates a DMA buffer, optionally copies host-to-controller payload, and restores controller-to-host data in `nvme_user_copy_cmd_complete()` before invoking the user callback.

- Implements transport ID and host ID parsing:
  - `spdk_nvme_transport_id_parse()`
  - `spdk_nvme_host_id_parse()`
  - `spdk_nvme_transport_id_compare()`
  - `spdk_nvme_transport_id_parse_trtype()`
  - `spdk_nvme_transport_id_parse_adrfam()`
  - `spdk_nvme_transport_id_populate_trstring()`
  - `spdk_nvme_trid_populate_transport()`

## Probe and Connection Flow

The central probe path is:

1. Caller enters `spdk_nvme_probe_ext()` or `spdk_nvme_probe_async_ext()`.
2. `nvme_driver_init()` ensures global shared driver state exists.
3. `nvme_probe_ctx_init()` initializes callback pointers and tail queues.
4. `nvme_probe_internal()` validates transport availability, locks the global driver, and calls `nvme_transport_ctrlr_scan()`.
5. For each found device, `nvme_ctrlr_probe()` either:
   - Reuses an existing controller matching transport ID and host NQN, increments the process ref count, and calls `attach_cb()`, or
   - Constructs a new transport controller and places it on `probe_ctx->init_ctrlrs`.
6. `spdk_nvme_probe_poll_async()` repeatedly calls `nvme_ctrlr_poll_internal()` for initializing controllers.
7. When a controller reaches `NVME_CTRLR_STATE_READY`, it is moved to either the shared PCIe list or per-process list, ref-counted for the current process, and delivered to `attach_cb()`.

The direct-connect path uses the same machinery but sets `direct_connect=true` and, when options are supplied, uses `nvme_connect_probe_cb()` to copy caller options into the controller opts used during construction.

## Detach Flow

Detach is ref-count aware and multi-process aware:

1. `nvme_ctrlr_detach_async()` locks the global driver and checks `nvme_ctrlr_get_ref_count()`.
2. If the current process holds the last reference:
   - Allocates `nvme_ctrlr_detach_ctx`.
   - Drops this process ref.
   - Sends I/O message detach notification through `nvme_io_msg_ctrlr_detach()`.
   - Starts `nvme_ctrlr_destruct_async()`.
3. If other processes still reference the controller:
   - Only drops this process ref and returns no destruction context.
4. Completion removes the controller from the shared/per-process attached list in `nvme_ctrlr_detach_async_finish()`.

## Transport ID Parsing Details

The parser accepts whitespace-separated `key:value` or `key=value` entries. Recognized transport ID keys include:

- `trtype`
- `adrfam`
- `traddr`
- `trsvcid`
- `priority`
- `subnqn`

It silently ignores application/custom keys such as `hostaddr`, `hostsvcid`, `hostnqn`, `ns`, and `alt_traddr`. Unknown keys are logged but do not cause a hard parse failure unless token parsing itself fails.

`spdk_nvme_transport_id_compare()` normalizes PCI addresses for PCIe comparisons. For IPv4/IPv6 fabrics addresses it uses `spdk_net_compare_address()` rather than raw string comparison, while other address families use case-insensitive string comparison for `traddr`/`trsvcid` and exact string comparison for `subnqn`.

## State, Concurrency, and Multi-Process Behavior

- Uses a process-private init mutex to serialize first-time global driver setup.
- Uses `g_spdk_nvme_driver->lock` as a robust process-shared mutex protecting shared controller lists and driver initialization state.
- PCIe controllers are considered shared across processes; other transports are stored per process.
- Attach callbacks are invoked after dropping the global driver lock so users can safely call APIs that may reacquire the lock, including detach.
- Request timeout handling is per active process and skips admin commands submitted by other processes.

## Important Dependencies

- `nvme_internal.h` for controller/qpair/request internals.
- `nvme_io_msg.h` for cross-process controller update/detach messages.
- `spdk/env.h` for memzones, timing, allocation, and process role.
- `spdk/net.h` for address comparison.
- Transport hooks through `nvme_transport_ctrlr_scan()`, `nvme_transport_ctrlr_construct()`, and related transport dispatch.

## Error Handling and Risks

- Timeout handling marks pending completion status as timed out so callback-side cleanup can free memory later.
- `nvme_wait_for_completion_poll()` treats invalid PCIe CSTS reads as internal device errors.
- Secondary processes fail initialization if the primary process has not started or does not initialize within the global timeout.
- Transport ID parsing has mixed behavior: malformed token/length failures return `-EINVAL`, while unknown keys are logged but parsing continues.
- Detach depends on process ref counts and robust shared locking; incorrect ref ownership elsewhere can prevent destruction or prematurely destruct a shared controller.

## Filesystem/Virtualization Relevance

This file is part of the user-space NVMe storage substrate used by SPDK applications and virtualized storage stacks. It provides controller discovery, attach, detach, and address parsing needed by higher-level block-device and NVMe-oF integrations.
