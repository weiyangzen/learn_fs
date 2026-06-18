# File Research: sources/virtualization/nbdkit/plugins/curl/times.c

Optional timing collector for curl requests.

Key behavior:
- Enabled by debug flag `-D curl.times=1`.
- Uses modern `_T` curl timing infos when available.
- Accumulates name lookup, connection, SSL negotiation, pretransfer, first byte, total transfer, and redirect timings.
- `update_times` is called after each curl perform completion.
- `display_times` reports cumulative timing buckets at plugin unload.

Notable details:
- Uses `_Atomic curl_off_t` counters.
- Cumulative curl timings are converted into stage durations by subtracting the previous cumulative value.
