# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rtt.h

Defines the RTT estimator state and API.

Key structure:
- `struct rtt_info`: `srtt`, `rttvar`, and current `rto`, all in milliseconds.

Public API:
- `rtt_init`, `rtt_timeout`, `rtt_unclamped`, `rtt_notimeout`, `rtt_update`, `rtt_lost`.
- Extern globals `RTT_MIN_TIMEOUT` and `RTT_MAX_TIMEOUT`.

Usage contract:
- Callers allocate the `struct rtt_info`.
- Valid responses call `rtt_update`.
- Timeout observations call `rtt_lost` with the original timeout value used for that query.
