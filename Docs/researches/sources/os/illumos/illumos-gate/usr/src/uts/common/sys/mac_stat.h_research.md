# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_stat.h

Purpose: Declares MAC-layer statistics structures and kstat lifecycle helpers for flows, rings, SRSes, soft rings, drivers, and defunct lanes.

Key structures:
- `mac_rx_stats_t`: local, poll, interrupt, drop, chain-size, and input-error counters.
- `mac_tx_stats_t`: output bytes/packets/errors, descriptor block/unblock counters, and soft drops.
- `mac_misc_stats_t`: multicast/broadcast counters, TX errors, defunct lane stats, and link-protection drops.

Key APIs:
- `mac_misc_stat_create/delete()`
- `mac_ring_stat_create/delete()`
- `mac_srs_stat_create/delete()`, `mac_tx_srs_stat_recreate()`
- `mac_soft_ring_stat_create/delete()`
- `mac_driver_stat_create/delete()`, `mac_driver_stat_default()`
- ring stat getters for RX/TX.

Important detail: TX block and unblock counters are intended to match in healthy descriptor-flow behavior; mismatch indicates a lower-layer wakeup failure.

Relevance to subset A: Network infrastructure, not filesystem-specific.
