# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/ping.c

Implements ICMP echo RTT probing for DFS referral target selection. It caches both successful and failed host results for 60 seconds in a linked `Pingcache`.

`ping(host, timeout)` first checks cache, then opens an ICMP dial to the host and sends eight echo requests with a small payload. It validates type/code, sequence bytes, and payload contents on replies.

The first RTT is effectively smoothed into the rolling `rtt` calculation; the comment says the first result is ignored because route setup may skew it, but the arithmetic initializes `rtt` at `-1` and averages each observed interval.

Failures return `-1` and are cached too, which avoids repeatedly probing down DFS targets.

Used by `dfs.c` to choose among DFS referral target servers, with optional debug logging under the `dfs` debug flag.
