# File Research: sources/os/plan9/9front/sys/src/9/ip/ip.c

Implements core IPv4 input/output handling, routing dispatch, fragmentation, reassembly, and IP statistics for the `Fs` stack.

Key responsibilities:
- Initializes `IP` state and fragment queues in `ip_init()`.
- Enables/disables routing through `iprouting()`.
- Sends IPv4 packets through `ipoput4()`.
- Receives IPv4 packets through `ipiput4()`.
- Handles IPv4 fragmentation and reassembly.
- Exposes IP stats through `ipstats()`.
- Computes IPv4 header checksum through `ipcsum()`.

Important implementation details:
- `ipoput4()` fills IP headers, performs route lookup, chooses gateway, clamps TCP MSS when forwarding, handles loopback bypass, fragments if needed, and sends via `ipifcoput()`.
- If DF is set and fragmentation is required, it sends ICMP “fragmentation needed”.
- `ipiput4()` validates version, header length, checksum, and packet length, then decides whether to forward or deliver locally.
- Forwarding supports route translation via protocol `forward` callbacks and reassembly-before-forwarding for selected interfaces.
- Local delivery strips IPv4 options before protocol dispatch.
- Reassembly uses per-stack fixed fragment pools, ordered fragment queues, overlap trimming, timeout cleanup, and max-size checks.

Dependencies and integration:
- Uses route lookup (`v4lookup`), interface output (`ipifcoput`), ICMP errors, protocol dispatch (`Fsrcvpcol`, `Fsrcvpcolx`), and TCP MSS clamp.
- Initializes IPv6 side through `ip_init_6(f)`, defined elsewhere.

Research notes:
- This is the IPv4 data-plane center for the Plan 9 IP stack.
- Route hints are threaded through output to cache route and ARP decisions.
- Reassembly stores `Ipfrag` metadata at block base and requires careful block pointer adjustment.
