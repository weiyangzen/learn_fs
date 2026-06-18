# sources/test-tools/strace/bundled/linux/include/uapi/linux/tcp_metrics.h

## Purpose

Defines the generic netlink ABI for cached TCP destination metrics. strace uses it to decode the `tcp_metrics` family, metric ids, address attributes, Fast Open cache attributes, and list/delete commands.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports `TCP_METRICS_GENL_NAME`, version, `enum tcp_metric_index` for RTT, RTTVAR, ssthresh, cwnd, reordering, and usec RTT variants, a duplicated attribute-id mapping for nested metrics, top-level `TCP_METRICS_ATTR_*` values for IPv4/IPv6 destination/source addresses, age, TIME-WAIT timestamp data, metric values, Fast Open MSS/drop/cookie data, and command ids `TCP_METRICS_CMD_GET` and `TCP_METRICS_CMD_DEL`.

## Control Flow, State, and Integration

Runtime flow is generic netlink request/dump/delete against the kernel's TCP metrics cache. State persists in memory as learned per-destination metrics and Fast Open cache metadata, influencing future TCP connections.

## Risks and Test Signals

Risks include the historical misspelling `TCP_METRICS_A_METRICS_REODERING`, nested metric attribute confusion, IPv4 versus IPv6 address field decoding, and assuming metrics are per-socket instead of cached per destination. Test signals include family command decode, nested metric value output, source/destination address attributes, and Fast Open cookie/drop fields.
