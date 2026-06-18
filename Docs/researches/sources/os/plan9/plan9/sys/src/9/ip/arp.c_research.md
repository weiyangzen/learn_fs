# File Research: sources/os/plan9/plan9/sys/src/9/ip/arp.c

Address-resolution cache for Plan 9 IP stack, covering IPv4 ARP-style entries and IPv6 neighbor solicitation state.

Key behavior:
- `arpinit()` allocates per-`Fs` ARP state and starts `rxmitproc`.
- Uses fixed cache of 256 `Arpent` entries and 64 hash buckets.
- `arpget()` looks up a MAC address; if unresolved, creates/updates an `AWAIT` entry and queues outgoing blocks on the entry.
- `arpresolve()` completes an entry, copies MAC, marks `AOK`, removes IPv6 retransmit state, and returns queued packets.
- `arpenter()` inserts or refreshes learned entries and flushes queued packets through the interface medium writer.
- `arpwrite()` supports control operations: `flush`, `add`, and `del`.
- `arpread()` formats active entries in fixed-width lines.
- `rxmitsols()` handles IPv6 neighbor solicitation retransmits, expiration, and ICMP host-unreachable generation for dropped packets.
- `rxmitproc()` sleeps until retransmit/drop work exists, then schedules retransmits based on `ReTransTimer`.

The ARP object is per network `Fs`; media-specific resolution entry points are reached through `Medium` callbacks.
