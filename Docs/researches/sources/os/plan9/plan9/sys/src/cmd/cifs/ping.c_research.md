# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/ping.c

ICMP echo helper used by DFS target selection. Sends eight ICMP echo requests with payload validation, ignores the first result in the running RTT average, applies an alarm timeout, and caches both successes and failures for 60 seconds per host.

Returned RTT is used by `dfs.c` to prefer nearby referral targets. Debug output is emitted for DFS debugging.
