# File Research: sources/virtualization/spdk/lib/nvmf/nvmf.c

Read completely: yes, 2170 lines.

Purpose: core NVMe-oF target lifecycle, transport registry integration, referrals, poll groups, qpair disconnect handling, configuration dump, listen APIs, target pause/resume, and subsystem state propagation.

Major responsibilities:
- Tracks all NVMf targets in global `g_nvmf_tgts`.
- Creates/destroys targets and registers them as SPDK IO devices.
- Adds/removes transports across all poll-group channels.
- Creates and destroys poll groups and their per-transport poll groups.
- Handles qpair placement, qpair disconnect, qpair finalization, and controller destruction when last qpair is gone.
- Maintains discovery referrals and referral host allow-lists.
- Dumps target configuration as JSON RPC replay data.
- Propagates subsystem namespace/channel state into poll groups and emits namespace/ANA async events.

Referral handling:
- `spdk_nvmf_tgt_add_referral()` validates/normalizes subnqn, deduplicates by transport ID, creates a discovery log entry, initializes host policy, links referral, and sends discovery log notice.
- Referral host add/remove validates NQN and emits host-specific discovery notices.
- `spdk_nvmf_referral_host_allowed()` requires a valid host NQN and either `allow_any_host` or explicit host match.

Target lifecycle:
- `spdk_nvmf_tgt_create()` copies versioned opts, checks unique target name, enforces custom discovery callback presence when requested, initializes subsystems bit array, RB tree, mutex, lists, IO device registration, and running state.
- `spdk_nvmf_tgt_destroy()` removes target from global list and unregisters IO device.
- Destroy callback clears referrals, stops mDNS PRR, removes subsystem listeners, destroys subsystems, frees subsystem ID bitmap, then destroys transports sequentially.

Poll-group lifecycle:
- `nvmf_tgt_create_poll_group()` creates per-transport poll groups, allocates subsystem poll-group array, initializes queued request lists, adds existing subsystems, and links the group to the target.
- `nvmf_tgt_destroy_poll_group_qpairs()` disconnects all qpairs before dropping the IO channel reference.
- `nvmf_tgt_cleanup_poll_group()` destroys transport poll groups and releases namespace IO channels.

Qpair lifecycle:
- `spdk_nvmf_tgt_new_qpair()` asks transport for an optimal poll group, otherwise round-robins, increments unassociated count, and sends add work to that group thread.
- `spdk_nvmf_poll_group_add()` initializes qpair fields, adds it to the transport poll group, links it to the poll group, and marks it connecting.
- `spdk_nvmf_qpair_disconnect()` serializes disconnect with `disconnect_started`, bounces to the group thread if necessary, marks deactivating, drains outstanding work, aborts pending zcopy/AER, and eventually calls `_nvmf_qpair_destroy()`.
- Finalization removes qpair from transport and group, frees auth, invokes transport qpair fini, clears controller qpair bits, and destructs controller on the subsystem thread when no qpairs remain.

Subsystem/poll-group state:
- `poll_group_update_subsystem()` allocates namespace channel state, detects namespace add/remove/replacement/resize and ANA group changes, updates reservation info, and sends namespace/ANA async events to controllers on the current thread.
- Add subsystem clears stale queued requests, updates namespace channels, marks subsystem and namespace info active.
- Remove subsystem marks inactive, disconnects matching qpairs, then releases namespace channels and state.
- Pause subsystem waits for management or namespace IO counters to drain before marking paused.
- Resume subsystem refreshes namespace state, marks active, and replays queued requests via zcopy or normal exec.

Transport/listen behavior:
- `spdk_nvmf_tgt_add_transport()` creates transport poll groups on every target IO channel before linking the transport globally, with rollback on failure.
- Mixed `dif_insert_or_strip` values are deprecated but still allowed with a deprecation log.
- `spdk_nvmf_tgt_listen_ext()` validates opts, finds transport by `trstring`, copies versioned listen opts, and delegates to transport listen op.
- `spdk_nvmf_tgt_stop_listen()` delegates to transport stop-listen.

Configuration dump:
- Emits max subsystem and CRDT settings.
- Dumps transport creation RPCs.
- Dumps referrals.
- Emits batched subsystem creation, host addition, namespace addition, namespace-host visibility, and active listener addition RPCs.
- Listener dump includes transport-specific options, secure channel flag, and optional socket implementation.

Concurrency and ownership:
- Poll-group lists and counts use target mutex.
- Qpair state changes assert execution on the poll-group thread.
- Target transport add/remove uses `spdk_for_each_channel()`.
- Target destroy may re-enter while asynchronous subsystem destruction is in progress.
- Referrals and discovery changes assert app-thread execution.

Notable edge cases:
- `nvmf_tgt_destroy_cb()` frees referrals directly without freeing per-referral host lists, unlike explicit referral removal.
- `nvmf_tgt_destroy_poll_group_qpairs()` logs allocation failure but cannot report it through the destroy callback path.
- `spdk_nvmf_tgt_find_subsystem()` rejects non-null-terminated NQNs within max length before RB lookup.
- Removal and destroy loops retry by reposting messages while qpairs are still disconnecting, so progress depends on transport disconnect completion.

Dependencies:
- Central integration point for `ctrlr_discovery.c` referral filtering and discovery notices.
- Calls mDNS stop/update hooks from `mdns_server.c`.
- Transport-specific behavior is delegated through `transport.h` wrappers and registered transport ops such as FC.
