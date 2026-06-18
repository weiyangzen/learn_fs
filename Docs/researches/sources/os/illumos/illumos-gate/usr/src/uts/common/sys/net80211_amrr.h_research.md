# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/net80211_amrr.h

Adaptive Multi Rate Retry rate-control interface for net80211.

Key responsibilities:
- Defines global AMRR thresholds for minimum and maximum success counts.
- Defines per-algorithm settings in `struct ieee80211_amrr`.
- Defines per-node AMRR state with success count, recovery flag, success threshold, transmit count, and retry count.
- Declares node initialization and rate-choice functions.

Dependencies:
- Forward-declares `struct ieee80211_node`; used by 802.11 drivers/common code that track tx/retry statistics.

Notable risks:
- Rate adaptation quality depends on drivers maintaining accurate transmit and retry counters in `ieee80211_amrr_node`.
- Threshold tuning affects throughput and stability under changing radio conditions.
