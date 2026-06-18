# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/rtt.c

Implements UDP round-trip-time estimation for resend timeouts.

Core behavior:
- Global `RTT_MIN_TIMEOUT` defaults to 50 ms and `RTT_MAX_TIMEOUT` defaults to 120000 ms; comments state configuration may overwrite them.
- `rtt_init` starts `srtt` at zero, initializes `rttvar` from `UNKNOWN_SERVER_NICENESS / 4`, and computes the initial RTO.
- `calc_rto` computes `srtt + 4 * rttvar`, clamped to configured min/max.
- `rtt_update` uses the standard smoothed estimator: `srtt += delta / 8`, `rttvar += (abs(delta) - rttvar) / 4`.
- `rtt_lost` performs exponential backoff using the original timeout to prevent many simultaneous queries from multiplying the cached timeout repeatedly.
- `rtt_unclamped` returns the current timeout after fallback/backoff, otherwise returns raw `srtt + 4 * rttvar`.
- `rtt_notimeout` returns the clamped calculated RTO without timeout-backoff effects.

Integration points:
- Includes `iterator/iterator.h` for `UNKNOWN_SERVER_NICENESS`.
- Used by resolver infrastructure for server selection and retry timing.
