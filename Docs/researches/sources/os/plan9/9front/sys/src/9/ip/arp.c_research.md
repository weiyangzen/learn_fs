# File Research: sources/os/plan9/9front/sys/src/9/ip/arp.c

Implements the shared IPv4 ARP and IPv6 neighbor-discovery cache for one `Fs` IP stack instance. The cache stores `Arpent` entries indexed by IP address and interface, holds outbound packets while resolution is pending, and runs a retransmission/drop worker.

Key responsibilities:
- Initializes per-stack ARP state with `arpinit()`.
- Provides lookup/queue behavior through `arpget()`.
- Completes resolution through `arpresolve()` and `arpenter()`.
- Supports manual control through `arpwrite()` commands: `flush`, `add`, `del`, and `garp`.
- Provides formatted cache reading through `arpread()`.
- Retransmits IPv6 neighbor solicitations and times out IPv4 ARP waits in `rxmitproc()`.

Important implementation details:
- `Arp` contains a 64-bucket hash table, 256 fixed cache entries, separate retransmit chains for IPv6 and IPv4, and a drop queue.
- `newarpent()` evicts the least recently used cache slot based on `utime`.
- `arpget()` may return with the ARP write lock held; caller must continue with `arpcontinue()`, `arpresolve()`, or `arprelease()`.
- Pending packets are held as a `Block->list` chain, but `arpcontinue()` trims all but the last queued packet to avoid buildup.
- Timed-out packets are later converted to ICMP unreachable messages outside the ARP lock.
- Route hints can cache a successful `Arpent` in `Routehint.a`.

Dependencies and integration:
- Used by media layers such as `ethermedium.c`.
- Calls `v4lookup`, `v6lookup`, `ipifcoput`, `icmpnohost`, `icmpnohost6`, `icmpns6`, and `arpforme`.
- Relies on `Ipifc->ifcid` to detect stale interface references.

Research notes:
- ARP and NDP resolution are unified behind the same cache object.
- `arpforme()` centralizes the decision to answer for local non-tentative addresses or proxy routes.
- The design intentionally avoids sending ICMP drops while holding the ARP lock.
