# File Research: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9314, source bytes 262102, report `Docs/researches/chunks/chunk_sources_virtualization_spdk_module_bdev_nvme_bdev_nvme_c_1_1_9314_7b9a25617e12_research.md`
- chunk 2: lines 9315-9853, source bytes 15542, report `Docs/researches/chunks/chunk_sources_virtualization_spdk_module_bdev_nvme_bdev_nvme_c_2_9315_9853_f3bda01e974f_research.md`

## Chunk Research

### Chunk 1: lines 1-9314

# Chunk Research: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme.c lines 1-9314

## Scope

This chunk covers the NVMe bdev module from file start through the end of the concrete NVMe command wrappers and the beginning of config JSON helpers. It includes module registration, global options, controller/bdev/channel models, multipath I/O path selection, retry/error handling, reset/failover/reconnect, namespace population/depopulation, discovery, hotplug, public create/delete/options APIs, and command submission wrappers for NVM/ZNS/admin/passthrough/abort/copy.

The file continues after line 9314 with controller/config JSON emission, CUSE config, key reauthentication, I/O path JSON, discovery info JSON, logging, and tracing. Those are cross-chunk continuation points, not owned by this chunk except where helper entry points are declared or first entered.

## Main APIs And Entry Points

- `SPDK_BDEV_MODULE_REGISTER(nvme, &nvme_if)` registers the `nvme` bdev module with async fini, init/fini callbacks, config JSON callback, and per-I/O context size.
- Public controller enumeration and lookup APIs in this chunk include `nvme_bdev_ctrlr_get_by_name()`, `nvme_ctrlr_get_by_name()`, `nvme_bdev_ctrlr_for_each()`, `spdk_bdev_nvme_first_bdev_ctrlr()`, `spdk_bdev_nvme_next_bdev_ctrlr()`, `spdk_bdev_nvme_ctrlr_get_name()`, `spdk_bdev_nvme_ctrlr_first_ctrlr()`, `spdk_bdev_nvme_ctrlr_next_ctrlr()`, and `spdk_bdev_nvme_ctrlr_get_opts()`.
- Public lifecycle/configuration APIs include `spdk_bdev_nvme_create()`, `spdk_bdev_nvme_delete()`, `spdk_bdev_nvme_get_opts()`, `spdk_bdev_nvme_set_opts()`, `spdk_bdev_nvme_get_default_ctrlr_opts()`, `bdev_nvme_set_hotplug()`, `bdev_nvme_start_discovery()`, `bdev_nvme_stop_discovery()`, `bdev_nvme_set_preferred_path()`, and deprecated `spdk_bdev_nvme_set_multipath_policy()`.
- The bdev function table `nvmelib_fn_table` routes bdev operations to `bdev_nvme_submit_request_initial()`, `bdev_nvme_io_type_supported()`, channel acquisition, JSON info/config, module context, memory-domain reporting, accel sequence support, and device statistics.
- Internal control APIs wrap SPDK channel iteration: `nvme_ctrlr_for_each_channel()` and `nvme_bdev_for_each_channel()` allocate iterator contexts and call `spdk_for_each_channel()`.

## Core State

- `g_opts` is the module-wide `spdk_bdev_nvme_opts` default and runtime configuration: timeouts, keep-alive, retry counts, reconnect policy, transport knobs, interrupt/poll periods, statistics toggles, flush enablement, multipath defaults, DH-HMAC-CHAP digest/group masks, and acceleration support.
- `g_nvme_bdev_ctrlrs` is the top-level list of logical NVMe bdev controllers. Each `nvme_bdev_ctrlr` owns a controller name, a list of `nvme_ctrlr` transport/controller instances, and a list of `nvme_bdev` namespaces exposed as bdevs.
- `nvme_ctrlr` owns the SPDK NVMe controller handle, path list (`trids` and `active_path_id`), namespace RB tree, admin poller, reset/reconnect/detach pollers, ANA buffers/state, key references, OPAL device, memory-domain type cache, reference count, and state flags including `destruct`, `resetting`, `disabled`, `reconnect_is_delayed`, `pending_failover`, `in_failover`, `dont_retry`, `fast_io_fail_timedout`, `ana_log_page_updating`, and `io_path_cache_clearing`.
- `nvme_bdev` wraps `spdk_bdev` and tracks namespace references for multipath, bdev-level refcount, error stats, multipath policy/selector/min-I/O, OPAL support, and update-in-progress state.
- `nvme_ns` binds a namespace ID to an SPDK namespace object, parent controller, optional bdev, probe context, ANA state/group/timers, and depopulation/update flags.
- Per-channel state is split into `nvme_ctrlr_channel` with one `nvme_qpair`, and `nvme_bdev_channel` with a list of `nvme_io_path`, cached current path, round-robin counter, retry list/poller, multipath settings, and reset freeze flag.
- `nvme_bdev_io` is the per-bdev-I/O context. It stores extended NVMe command options, selected I/O path, submit timestamp, retry count/timer, primary and fused iovec cursors, saved completion, fused command state, zone-report buffer/progress, and retry queue linkage.
- Hotplug and discovery have global state: `g_skipped_nvme_ctrlrs`, hotplug pollers/probe context, and `g_discovery_ctxs`.

## Initialization And Teardown

- `bdev_nvme_init()` registers `g_nvme_bdev_ctrlrs` as an SPDK I/O device whose per-thread channels are NVMe poll groups, then marks `g_bdev_nvme_init_done`.
- `bdev_nvme_fini()` unregisters hotplug/probe state, frees skipped PCIe entries, stops discovery services if any are active, then destructs controllers. Final module completion occurs in `bdev_nvme_fini_done()` only after `g_bdev_nvme_module_finish` is set and all controllers are gone.
- Controller deletion is async. `nvme_ctrlr_delete()` unregisters reconnect/admin/interrupt resources, starts `spdk_nvme_detach_async()`, polls it in `nvme_detach_poller()`, then `_nvme_ctrlr_delete()` frees ANA buffers, OPAL, controller grouping, namespaces, path IDs, mutex/key refs, and the controller.
- Refcounting is explicit and mostly app-thread-owned. `nvme_ctrlr_put_ref()` asserts no reset/ANA/cache-clear operations remain at final release and unregisters the controller I/O device only when `destruct` is set.

## I/O Path And Multipath Control Flow

- Bdev channels are created by `bdev_nvme_create_bdev_channel_cb()`. They snapshot bdev multipath policy and add one `nvme_io_path` for each namespace path in `nbdev->nvme_ns_list`.
- `_bdev_nvme_add_io_path()` allocates an I/O path, gets a controller channel for the namespace controller, binds the path to that channel's `nvme_qpair`, inserts it into both qpair and bdev-channel lists, and clears the cached current path.
- `_bdev_nvme_delete_io_path()` removes the path from the bdev channel and releases the controller channel, but deliberately does not free the `nvme_io_path`; it is freed when the owning qpair is freed so in-flight completions can still update stats without use-after-free.
- Availability requires a connected qpair, no qpair failure reason, no channel reset in progress, an active namespace object, and ANA optimized or non-optimized state.
- `bdev_nvme_find_io_path()` supports active-passive and active-active. Active-passive caches the selected path. Active-active round-robin respects `rr_min_io`; queue-depth selection scans connected active paths and picks the lowest outstanding request count, preferring optimized ANA paths over non-optimized.
- `bdev_nvme_set_preferred_path()` reorders both the bdev namespace list and every bdev-channel I/O path list to prefer a controller by `cntlid`. This is a per-bdev multipath preference operation.
- Deprecated `spdk_bdev_nvme_set_multipath_policy()` validates policy/selector/min-I/O, updates `nvme_bdev`, then updates all open bdev channels and clears current-path caches.

## Submission, Completion, Retry, And Abort

- `bdev_nvme_submit_request_initial()` initializes submit timestamp and retry count, then calls `bdev_nvme_submit_request()`.
- `bdev_nvme_submit_request()` records a trace start, selects an I/O path, fails non-admin I/O immediately with `-ENXIO` if no path exists, and lets admin I/O continue because admin passthrough scans controllers itself.
- `_bdev_nvme_submit_request()` dispatches bdev I/O types to concrete wrappers: read/write/compare/compare-and-write/unmap/write-zeroes/reset/NSSR/flush/ZNS append/get zone info/zone management/NVMe admin/NVMe I/O passthrough/abort/copy/write-uncorrectable. Nonzero immediate return codes are completed through `bdev_nvme_io_complete()`.
- `bdev_nvme_io_complete_nvme_status()` updates per-path stats on success, updates NVMe error stats on failure, applies DNR/abort/retry-count checks, refuses to retry accel sequences, then either queues a retry or completes with NVMe status.
- Retry decisions are in `bdev_nvme_check_retry_io()`. Path errors, ANA errors, qpair unavailability, and controller unavailability clear path caches and can trigger an ANA log update. If any path may become available, retries are scheduled immediately or after command retry delay (`crd`) converted from controller data.
- Immediate `-ENXIO` completions can be queued for retry if retry count allows and any path may become available. Retry queue entries are ordered by `retry_ticks` and driven by a per-channel poller.
- `bdev_nvme_abort()` first removes a matching queued retry I/O. Otherwise it uses `spdk_nvme_ctrlr_cmd_abort_ext()` against the original I/O path if known, or scans paths with qpair `NULL` if the original path is unknown.
- `bdev_nvme_abort_retry_ios()` aborts all queued retry I/O during channel destruction or bdev reset freeze/unfreeze.

## Reset, Failover, Disable, And Reconnect

- Controller reset state is orchestrated on the app thread. `bdev_nvme_get_reset_ctrlr_fn()` refuses destructed, already resetting, or disabled controllers, grabs a ref, sets `resetting`/`dont_retry`, records reset start time, and returns either a reconnect-now or full reset function.
- A full reset destroys/disconnects qpairs across all controller channels, disconnects fabrics controllers where needed, calls `spdk_nvme_ctrlr_reconnect_async()`, polls reconnect, checks namespace activity, recreates qpairs, then completes pending resets.
- `bdev_nvme_reset_ctrlr_complete()` centralizes reset completion: handles alternate TRID failover, pending bdev reset I/Os, fast-I/O-fail timeout, callback delivery, ref release, delayed reconnect, controller destruction on controller-loss timeout, or pending failover.
- `bdev_nvme_start_ctrlr_failover()` marks or rotates to the next alternate path using `bdev_nvme_failover_trid()`, handles already-resetting controllers through `pending_failover`, and invokes reset to connect the new active TRID.
- `bdev_nvme_enable_ctrlr()` reconnects a disabled controller; `bdev_nvme_disable_ctrlr()` destroys qpairs and disconnects or cancels delayed reconnect, then marks the controller disabled and pauses admin polling.
- Bdev reset I/O freezes all bdev channels, walks every I/O path/controller sequentially, queues behind in-progress controller resets when needed, then unfreezes channels and aborts retry queues. The source contains an explicit TODO noting a bug: cached `bio->io_path` can be removed from a channel list during namespace depopulate, causing undefined behavior.

## Poll Groups, Qpairs, Interrupts, And Acceleration

- `bdev_nvme_create_poll_group_cb()` creates an SPDK NVMe poll group per SPDK thread/channel, registers `bdev_nvme_poll()`, and, in interrupt mode, binds fd-group interrupt handling.
- `bdev_nvme_poll()` calls `spdk_nvme_poll_group_process_completions()`, handles disconnected qpairs through `bdev_nvme_disconnected_qpair_cb()`, tracks spin time when VTune support enables it, and clears path caches on negative poll results.
- `nvme_qpair_create()` allocates a wrapper, gets a poll-group channel, optionally creates/connects an SPDK I/O qpair, tolerates creation failure only when reconnect delay and bdev retry policy can cover it, then links it to poll group and controller channel.
- `bdev_nvme_create_qpair()` configures async qpair creation outside interrupt mode, applies `delay_cmd_submit`, ensures `io_queue_requests`, adds the qpair to its poll group, connects it, and clears path caches unless auto-failback is disabled.
- Acceleration support is exposed to the NVMe library through `g_bdev_nvme_accel_fn_table`, which delegates CRC32C/copy sequence steps to the SPDK accel framework using a lazily acquired accel channel on the poll group.

## Namespace And Bdev Population

- `nvme_ctrlr_create()` constructs a controller wrapper, copies key references from probe context, creates the initial path ID, caches memory-domain types, rejects OCSSD, initializes options, admin poller/interrupt, timeout callback, remove callback, OPAL device, logical bdev-controller grouping, ANA support, and controller I/O-device registration.
- `nvme_ctrlr_create_done()` registers AER and namespace-attribute callbacks only after controller registration, then populates namespaces.
- `nvme_ctrlr_populate_namespaces()` either full-scans active namespaces or processes an NVMe changed namespace list. Existing namespaces are updated or depopulated; new active namespaces are allocated, inserted in the RB tree, and populated.
- `nvme_bdev_create()` creates a bdev for a namespace, initializes multipath policy from controller options, fills bdev geometry/capabilities through `nbdev_create()`, registers the bdev as an I/O device, links namespace/bdev/controller structures, and registers the public bdev.
- Multipath namespace attachment uses `nvme_bdev_add_ns()`: it requires `nmic.shrns`, verifies identity with existing namespace by NGUID/EUI64/UUID/CSI, increments bdev refcount, links the namespace, and dynamically adds I/O paths to open bdev channels.
- Namespace depopulation decrements bdev refcount, unregisters the bdev on last namespace, or removes just that namespace and dynamically deletes paths from open channels before removing from the controller RB tree.
- Namespace resize is detected in `nvme_ctrlr_update_ns()` and reported through `spdk_bdev_notify_blockcnt_change()`.
- `nbdev_create()` maps NVMe identify data to SPDK bdev fields: product name, ZNS geometry, UUID/NGUID/generated UUID, write cache, block length/count, max xfer and segments, optimal boundaries, physical block size, DIF/DIX metadata and PI settings, compare-and-write unit, copy limits, NUMA ID, unmap/write-zeroes limits, and function table/module pointers.

## ANA Handling

- ANA is initialized if controller data advertises ANA reporting. `nvme_ctrlr_init_ana_log_page()` allocates a DMA log-page buffer and an aligned copy buffer for descriptors, issues `GET LOG PAGE`, and calls `nvme_ctrlr_create_done()` only after initial ANA states are read.
- `bdev_nvme_parse_ana_log_page()` iterates descriptors by copying each descriptor into the temporary buffer because descriptors may be unaligned.
- `_nvme_ns_set_ana_state()` updates namespace ANA group/state and clears `ana_state_updating`. Optimized/non-optimized states cancel transition timers; inaccessible/change states start an ANATT timer that marks `ana_transition_timedout`.
- AER callback `nvme_ctrlr_aer_cb()` triggers ANA log reread on ANA change notices. Retry paths can also request ANA updates on ANA errors.
- Failed ANA reads disable ANA log-page use, free the ANA buffer, reset namespaces to optimized, and clear update flags.

## Discovery, Hotplug, Create, And Delete

- `spdk_bdev_nvme_create()` validates duplicate TRID/hostnqn, controller name length, resiliency and multipath options, allocates an async probe context, copies driver/bdev options, loads keyring keys for PSK/DH-HMAC-CHAP, enables interrupts for PCIe/RDMA if global interrupt mode is active, chooses attach-vs-failover callback, starts `spdk_nvme_connect_async()`, and polls it with `bdev_nvme_async_poll()`.
- Multipath creation with the same base name creates another `nvme_ctrlr`; non-multipath same-name creation adds a secondary failover TRID after validating transport type, subnqn, duplicate path absence, and namespace identity.
- `spdk_bdev_nvme_delete()` matches path IDs with wildcard-like zero fields, removes inactive alternate paths directly, destructs a controller if its only active path is removed, or starts failover if an active path has alternates. Optional callback completion is polled until the path disappears or a 10-second timeout expires.
- PCIe hotplug uses `bdev_nvme_set_hotplug()`, `bdev_nvme_hotplug()`, `bdev_nvme_hotplug_probe()`, `hotplug_probe_cb()`, and `attach_cb()`. Explicitly deleted PCIe controllers are recorded in `g_skipped_nvme_ctrlrs` so hotplug does not immediately reattach them.
- Discovery services use `discovery_ctx` and `discovery_entry_ctx`. They connect to discovery controllers, read discovery log pages, start bdev NVMe creates for NVM subsystem entries, support additional discovery entries, remove missing controllers, handle discovery AERs, and stop by deleting discovered NVM controllers and detaching the discovery controller.

## Concrete NVMe Command Wrappers

- PI/DIF error diagnostics are handled by `bdev_nvme_verify_pi_error()`. Read PI errors can trigger a second read without PI checking via `bdev_nvme_no_pi_readv()` before completing with the original error.
- Read/write use `spdk_nvme_ns_cmd_read_iov()` and `spdk_nvme_ns_cmd_write_iov()` with `spdk_nvme_ns_cmd_ext_io_opts`, memory domains, metadata, DIF flags, accel sequence, and write directive fields.
- Zone append uses single-buffer or vectored ZNS append APIs and stores the appended LBA into `offset_blocks` from completion `cdw0` before bdev completion.
- Compare and fused compare-and-write maintain primary/fused iovec cursors and completion state; compare failure takes precedence over write completion status.
- Unmap builds one or more DSM ranges with NVMe maximum range/count limits and submits Dataset Management deallocate.
- Write zeroes enforces the 16-bit NLB protocol limit before calling `spdk_nvme_ns_cmd_write_zeroes()`.
- ZNS get-zone-info allocates a report buffer sized by max I/O xfer, validates zone alignment/count, may issue multiple zone reports, converts NVMe zone descriptors to bdev zone info, and frees the buffer on all completion paths.
- Admin passthrough selects the first available controller path and validates transfer size against controller MDTS. I/O passthrough fills `cmd->nsid`, validates nbytes/metadata size, and submits raw buffer or iov raw commands.
- Copy submits a single-source-range NVMe copy command because the bdev interface only supports one segment here.

## Dependencies

- SPDK bdev core: module registration, bdev registration/unregistration, I/O completion/status, bdev channel iteration, stats, block count notification, buffer acquisition, and bdev descriptors.
- SPDK NVMe library: controller connect/detach/reconnect/disconnect, qpair allocation/connect/disconnect/free, poll groups, completions, namespace commands, raw passthrough, AER/ns callbacks, timeout callbacks, discovery log page, ANA log page, ZNS helpers, copy/write-uncorrectable/Dataset Management, transport IDs/options, CUSE hooks in adjacent code, and controller/namespace identify data.
- SPDK threading/polling/interrupts: app-thread assertions, `spdk_thread_send_msg()`, poller registration/pause/resume/unregister, interrupt registration/fd groups, and per-thread I/O devices.
- SPDK accel and memory-domain APIs: acceleration sequence hooks, CRC32C/copy, memory-domain reporting and type comparison.
- SPDK DIF/DIX, keyring, OPAL, JSON, trace/DTrace/logging, endian/net/string/uuid utility APIs.

## Risks And Invariants

- Most mutable controller/bdev topology operations assert app-thread context. Violating this would race RB/TAILQ/STAILQ structures and refcounts.
- `nvme_ctrlr_put_ref()` relies on operation flags being set after ref get and cleared before ref put. Final release asserts no reset/ANA/cache-clear is active and `destruct` is true.
- `_bdev_nvme_delete_io_path()` intentionally defers freeing paths until qpair deletion. Any new path lifetime changes must preserve completion-time stats safety.
- Reset I/O has a known TODO risk: cached `bio->io_path` can be removed during namespace depopulation, leading to undefined behavior.
- Retry of accel sequences is disabled because the sequence execution state cannot be known safely after an error.
- `bdev_nvme_comparev_and_writev()` logs unexpected write success after compare failure and returns compare status; its immediate write-submission error path treats non-ENOMEM write submission errors as `rc = 0`, relying on compare/write completion semantics.
- ANA parsing copies descriptors using a shrinking `copy_len`; correctness depends on controller-reported ANA log page size and descriptor counts being sane after earlier size checks.
- Discovery `discovery_log_page_cb()` returns without completing discovery on log-page errors, leaving state recovery to poller/admin failure paths.
- `spdk_bdev_nvme_set_opts()` is rejected after init once controllers exist, so runtime option changes are intentionally constrained.

## Cross-Chunk References

- `bdev_nvme_write_multipath_config()` and `bdev_nvme_opts_config_json()` begin near the end of this chunk and continue into adjacent config JSON helpers after line 9314. The final config emitter `bdev_nvme_config_json()` is outside this chunk.
- The chunk calls/defines helpers that are likely exposed through headers/RPC modules outside this file: create/delete/options/discovery/preferred-path/controller-op APIs.
- Post-9314 code continues with controller config JSON, hotplug/multipath JSON, key reauthentication (`bdev_nvme_set_keys()`), I/O path JSON (`nvme_io_path_info_json()`), discovery info JSON, log registration, and trace registration.

### Chunk 2: lines 9315-9853

# Chunk Research: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme.c lines 9315-9853

## Scope And Position

This chunk covers the end of `module/bdev/nvme/bdev_nvme.c`. It begins in the body of the optional CUSE config dump helper and ends at file end with SPDK trace registration. The code belongs to the SPDK NVMe bdev module in subset A, under virtualization/block-device integration.

The chunk is mostly control-plane code rather than data-path I/O submission. It serializes live NVMe bdev configuration to JSON/RPC replay records, exposes controller and discovery status helpers, updates DH-HMAC-CHAP keys with asynchronous authentication, and registers trace metadata for NVMe bdev I/O.

## APIs And Entry Points

- `bdev_nvme_config_json(struct spdk_json_write_ctx *w)` is the module `.config_json` callback wired earlier in the file through `nvme_if.config_json`.
- `bdev_nvme_get_ctrlr(struct spdk_bdev *bdev)` returns the underlying `struct spdk_nvme_ctrlr *` for an NVMe bdev.
- `bdev_nvme_set_keys(...)` is the exported asynchronous DHCHAP key-update/authentication path for a named NVMe bdev controller group.
- `nvme_io_path_info_json(...)` serializes one I/O path status object.
- `bdev_nvme_get_discovery_info(...)` emits active discovery contexts and referral transport IDs.
- `bdev_nvme_trace()`, registered by `SPDK_TRACE_REGISTER_FN`, publishes trace object/point metadata for bdev NVMe I/O.
- Under `SPDK_CONFIG_NVME_CUSE`, `nvme_ctrlr_cuse_config_json()` emits `bdev_nvme_cuse_register` replay RPCs only if CUSE controller-name lookup succeeds.

## Control Flow And State

`bdev_nvme_config_json()` dumps global NVMe bdev options, batches `bdev_nvme_attach_controller` records for all controller paths in `g_nvme_bdev_ctrlrs`, then emits dependent configuration individually: CUSE registration, bdev multipath policy overrides, discovery service RPCs, mDNS discovery config, and finally hotplug settings.

`nvme_ctrlr_config_json()` suppresses discovery-owned controllers, because those are restored via discovery RPCs. Explicit controllers include transport ID, PI check flags, timeout settings, optional PSK/DHCHAP key names, host options, digest settings, source address/service, queue count, fabrics timeout, and multipath options.

`bdev_nvme_set_keys()` allocates a context, gets keyring references, finds the named controller group, obtains live controller refs with `bdev_nvme_next_ctrlr()`, and authenticates controllers serially. For each controller it calls `spdk_nvme_ctrlr_set_keys()`, optionally authenticates the controller, then iterates connected qpairs with `spdk_for_each_channel()` and `spdk_nvme_qpair_authenticate()`. Completion releases refs, puts keys, and invokes the caller callback.

`nvme_io_path_is_current()` depends on path availability first. In active-active multipath, optimized ANA paths are current; non-optimized paths are current only when no optimized path exists. Other policies compare against `nbdev_ch->current_io_path`.

## Dependencies And Risks

Dependencies include SPDK JSON writers, NVMe controller/qpair APIs, keyring APIs, app-thread/channel iteration, CUSE APIs when enabled, trace registration, TAILQ/STAILQ lists, and local helpers from earlier chunks such as `nvme_bdev_dump_trid_json`, `bdev_nvme_write_multipath_config`, `nvme_io_path_is_available`, and controller refcount helpers.

Key risks:
- Config dump asserts `active_path_id` is the first transport path.
- Discovery-owned controllers are omitted from attach replay, so discovery config ordering matters.
- Hotplug is emitted last to avoid reconstruct-time races.
- `bdev_nvme_get_ctrlr()` asserts the bdev has at least one namespace.
- `bdev_nvme_set_keys()` assumes a valid callback.
- Disconnected qpairs are skipped during immediate authentication and must be handled by reconnect/reset paths elsewhere.
- `nvme_io_path_info_json()` assumes fully initialized `io_path`, qpair, namespace, and controller pointers.

## Cross-Chunk References

- This chunk starts mid-`nvme_ctrlr_cuse_config_json()`; its header/local declarations are immediately before line 9315.
- Module registration, global queue definitions, controller lookup, refcounting, path availability, and discovery setup are earlier in the file.
- Previous chunk code defines global options JSON and discovery/mDNS config helpers used here.
- Earlier data-path functions emit the tracepoints whose descriptions and NVMe lower-layer relations are registered at the end of this chunk.
