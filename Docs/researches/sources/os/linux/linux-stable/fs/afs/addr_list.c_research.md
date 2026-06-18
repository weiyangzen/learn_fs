# File Research: sources/os/linux/linux-stable/fs/afs/addr_list.c

This file manages AFS server address lists and DNS-derived VL server address records.

Major responsibilities:
- Allocates, refcounts, RCU-frees, and traces `struct afs_addr_list`.
- Parses delimited textual IPv4/IPv6 address lists with optional `+port` suffixes.
- Builds a one-server VL server list around parsed explicit addresses.
- Queries DNS `afsdb` data for a cell and converts the resolver result into a VL server list.
- Merges IPv4 and IPv6 endpoints into ordered RxRPC peer lists.
- Maintains RxRPC peer appdata backpointers when a server’s address list changes.

Address parsing:
- `afs_parse_text_addrs()` accepts delimiter-separated address strings and adapts `:` delimiter to comma when necessary for IPv6-like input.
- IPv6 addresses can be bracketed.
- Each parsed address is converted with `in4_pton()` or `in6_pton()`.
- Ports are parsed from `+1234`, with range checking.
- Invalid syntax returns `-EINVAL` with trace/debug problem markers; empty input returns `-EDESTADDRREQ`.

Address list ordering:
- IPv4 peers are stored before IPv6 peers.
- Within each family group, peers are sorted by peer pointer.
- Duplicate peers are detected and dropped by releasing the newly looked-up peer.
- Lists cap at `AFS_MAX_ADDRESSES`.

DNS behavior:
- `afs_dns_query()` asks the DNS resolver for `afsdb` data with `srv=1`.
- Resolver output beginning with a NUL record is passed to `afs_extract_vlserver_list()`.
- Plain text output is parsed as comma-separated addresses.
- Zero DNS expiry is normalized to a short default future expiry.

Peer appdata:
- `afs_set_peer_appdata()` sets or clears per-peer appdata for new, removed, or retained peers by walking old and new ordered lists.
- This lets incoming RxRPC/cache-manager security paths recover the owning `afs_server` from peer data.
