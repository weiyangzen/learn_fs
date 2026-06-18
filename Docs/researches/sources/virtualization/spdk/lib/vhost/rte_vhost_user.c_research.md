# File Research: sources/virtualization/spdk/lib/vhost/rte_vhost_user.c

This file adapts DPDK vhost-user to SPDK vhost sessions. It owns guest physical address translation, split and packed virtqueue traversal, used-ring updates, interrupt/coalescing behavior, VM memory registration, session lifecycle, vhost-user message hooks, Unix socket registration, and shutdown coordination.

Address translation uses `rte_vhost_va_from_guest_pa()`. `vhost_gpa_to_vva()` requires the entire requested range to translate. Descriptor-to-iovec helpers split guest physical ranges into host iovecs and enforce `SPDK_VHOST_IOVS_MAX`.

Split-ring helpers read available ring entries, handle indirect descriptor tables, walk descriptor chains, log dirty pages when `VHOST_F_LOG_ALL` is negotiated, enqueue used-ring entries, update inflight tracking, and signal used vrings. Packed-ring helpers detect indirect descriptors, walk descriptor lists, restore/wrap avail and used indices, enqueue used packed descriptors, manage packed ring phase bits, and clear inflight descriptors.

Interrupt signaling is handled by `vhost_session_vq_used_signal()`. Without coalescing, it checks event suppression flags and calls DPDK’s nonblocking vring call when available. With coalescing, it updates per-queue request counters and delays interrupts based on configured delay and IOPS threshold. In interrupt mode, available-ring reads drain kickfds and may re-kick if unprocessed requests remain.

VM memory handling registers guest memory with SPDK for vtophys translation. `vhost_session_mem_register()` rounds mmap ranges to 2 MiB boundaries and skips duplicate starts; unregister mirrors that. `vhost_register_memtable_if_required()` fetches the DPDK memory table, detects changes against the current table, unregisters old memory, registers new memory, or frees unchanged tables.

Session lifecycle starts in `new_connection()`, which maps DPDK `vid` to a controller name, allocates a cache-line-aligned `spdk_vhost_session` plus backend session context, initializes semaphore/state, inserts it into the device session list, and installs DPDK extern message hooks. `start_device()` schedules backend `start_session()` on the vhost device thread after memory is present. `_stop_session()` waits for backend stop, saves vring bases, and clears queue state. `destroy_connection()` stops if needed, unregisters memory, removes the session, and frees it.

`enable_device_vq()` initializes one virtqueue from DPDK state, restores vring base and packed inflight state, allocates backend queue tasks, configures notification suppression according to interrupt mode, optionally calls backend `enable_vq()`, and updates session queue count. `set_device_vq_callfd()` forces an interrupt after migration/restart by incrementing used request count.

The DPDK callback table maps new/destroy device events to SPDK start/stop and new/destroy connection events to session allocation/free. Extern pre-message hooks stop running sessions before `GET_VRING_BASE` or memory-table replacement and delegate GET/SET_CONFIG to backend callbacks. Post-message hooks record negotiated features, initialize queues on `SET_VRING_KICK`, update callfds, register memory on `SET_MEM_TABLE`/`ADD_MEM_REG`, and restart sessions after memory replacement.

`vhost_register_unix_socket()` owns vhost-user socket registration: it unlinks stale socket files, rejects non-socket path collisions, registers the DPDK driver, sets enabled/disabled virtio features, registers callbacks, ORs protocol features, and starts the driver. Wrapper functions expose DPDK memory-table, unregister, and feature-query calls.

Device-level APIs manage coalescing, socket base path, device initialization/start/create, busy checks, unregister, vhost-user subsystem init/fini, and JSON session info. `vhost_user_fini()` starts a detached shutdown thread because DPDK socket removal can synchronously call SPDK callbacks and would otherwise deadlock.

Important invariants are lock ordering between global vhost lock and per-device session lock, not blocking SPDK callback threads during DPDK shutdown, preserving vring indices and packed phase bits across stop/restart, memory registration consistency, and backend start/stop completion through semaphores.
