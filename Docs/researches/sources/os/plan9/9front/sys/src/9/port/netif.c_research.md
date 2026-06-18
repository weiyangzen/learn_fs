# File Research: sources/os/plan9/9front/sys/src/9/port/netif.c

Generic multiplexed network-interface file hierarchy and common network helper routines.

Key responsibilities:
- Initializes `Netif` instances and allocates `Netfile` slots.
- Provides a three-level devfs hierarchy with interface directory, `clone`/`addr`/`stats`/`ifstats`, and per-conversation `data`/`ctl`/`type`.
- Implements open/read/bread/write/wstat/stat/close helpers for network devices.
- Handles control commands: `connect`, `promiscuous`, `scanbs`, `bridge`, `bypass`, `headersonly`, `addmulti`, and `delmulti`/`remmulti`.
- Tracks per-open ownership and permissions.
- Manages multicast address reference counts and hardware callback transitions.
- Provides host/network byte-order helpers: `hnputv`, `hnputl`, `hnputs`, `nhgetv`, `nhgetl`, `nhgets`.

Important behavior:
- `clone` opens allocate or reuse a free conversation and redirect the channel to its `ctl`.
- `connect <type>` rejects duplicate positive types; negative types count as “all.”
- Promiscuous/scanning callbacks are enabled when first requested and disabled when last user closes.
- Per-conversation multicast tracking uses a fixed 64-bit bitmask, while interface multicast addresses are held in a linked list and hash table.

Notable risks:
- `netifclose()` iterates multicast addresses with an index variable that is not visibly incremented in the loop, so cleanup relies on current code behavior and deserves care if edited.
- The control parser truncates writes to a 63-byte local buffer.
