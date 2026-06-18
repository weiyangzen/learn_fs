# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_soft_ring.h

Purpose: Defines MAC soft rings and soft ring sets, the queueing, fanout, worker/polling, flow-control, and quiesce/restart machinery used by GLDv3 receive/transmit scaling.

Key structures:
- `mac_soft_ring_t`: per-lane queue with lock, packet chain, TX watermarks, RX callback, worker thread, CPU binding, stats, teardown state, and parent SRS pointer.
- `mac_soft_ring_set_t`: shared Rx/Tx queue/controller with SRS type/state flags, ring arrays, bandwidth control, CPU binding, poll/worker threads, client/flow/ring backpointers, and embedded `mac_srs_rx_t`/`mac_srs_tx_t`.
- `mac_srs_rx_t`: receive-side callbacks, polling thresholds, high/low watermarks, and many poll/drain counters.
- `mac_srs_tx_t`: transmit mode, TX function, hardware ring/group pointers, queue thresholds, stats, aggregation ring mapping.

State model:
- `mac_soft_ring_state_t` separates immutable `ST_RING_*` traits from live `S_RING_*` processing, blocking, blanking, quiesce, restart, and condemn flags.
- `mac_soft_ring_set_type` describes static or administrative traits such as link/flow, Tx/Rx, no soft rings, protocol fanout, latency optimization, default group, bandwidth control, DLS bypass, and client polling.
- `mac_soft_ring_set_state_t` captures live SRS processing state: worker/poll ownership, polling mode, TX blocking/high-water, client processing, quiesce/restart/condemn, and global-list membership.

Key macros and APIs:
- `MAC_SRS_POLLING_OFF`, `MAC_COUNT_CHAIN`, and `MAC_UPDATE_SRS_COUNT_LOCKED` encode hot-path queue/poll transitions.
- Exports creation, destruction, wakeup, polling, DLS bypass, client polling, quiesce/restart, fanout setup, TX SRS setup, ring add/delete, bandwidth updates, and worker drain routines.

Important details:
- The file documents strict ownership around `SRS_PROC`/`S_RING_PROC` and lock release while processing packets.
- Quiesce/condemn/restart is explicit at both SRS and soft-ring level, with condition variables and counters for teardown synchronization.
- Receive polling tracks packets queued between SRS and soft rings so hardware interrupt re-enable decisions account for backlog not yet delivered to clients.

Relevance to subset A: Not filesystem code, but important illumos kernel scheduling/queueing infrastructure.
