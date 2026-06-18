# File Research: sources/os/plan9/9front/sys/src/9/ip/igmp.c

Implements IPv4 IGMPv1/v2 group reporting and IPv6 MLDv1 reporting. It registers both `igmp` and `mld` protocols and manages delayed multicast reports.

Key responsibilities:
- Sends IGMP reports/leaves through `igmpsendreport()`.
- Sends MLD reports/done messages through `mldsendreport()`.
- Queues randomized delayed reports in `queuereport()`.
- Cancels pending reports when another host reports the same group through `purgereport()`.
- Processes inbound IGMP in `igmpiput()` and MLD in `mldiput()`.
- Exposes `multicastreportfn` used by interface multicast membership changes.

Important implementation details:
- `Priv` contains a hash table of pending `Report` objects and a `Rendez` for the report worker.
- `igmpproc()` wakes when reports are pending, ages timeouts, sends expired reports, and sleeps at 100 ms ticks.
- MLD messages include an IPv6 hop-by-hop Router Alert option.
- MLD reports are only sent for valid multicast groups with appropriate scope and not for all-nodes link-local.
- IGMP checksum covers only the IGMP header portion after the IPv4 header.

Dependencies and integration:
- Sends through `ipoput4()` and `ipoput6()` with TTL/hop limit 1.
- Uses `ipifcgetmulti()` to enumerate matching interface multicast memberships.
- Shares one `Priv` between IGMP and MLD protocols.

Research notes:
- This file handles multicast membership signaling, not packet delivery.
- MLD input strips and validates the hop-by-hop option header before treating the payload as ICMPv6-like MLD.
