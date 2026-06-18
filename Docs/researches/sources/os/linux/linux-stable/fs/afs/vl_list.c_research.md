# File Research: sources/os/linux/linux-stable/fs/afs/vl_list.c

## Scope

Allocates VL-server records/lists and parses DNS server-list payloads into AFS VL server/address structures.

## APIs And Behavior

- `afs_alloc_vlserver()` and `afs_put_vlserver()` manage named VL server records with locks, probe state, service ID, port, and address list.
- `afs_alloc_vlserver_list()` and `afs_put_vlserverlist()` manage ordered VL server lists.
- `afs_extract_vl_addrs()` parses IPv4/IPv6 DNS address records and builds an address list, preferring IPv6 when available.
- `afs_extract_vlserver_list()` validates DNS server-list v1 payloads, reuses existing server records by name/port, updates address lists, sorts entries by priority then weight, and records DNS source/status.

## State And Dependencies

Depends on DNS payload structures, address merge helpers, cell `vl_servers`, and RCU-managed address-list replacement. Existing VL server lists are consulted to preserve server objects across DNS refreshes.

## Risks And Invariants

Payload parsing must advance over names and addresses even when some entries are unusable. Empty address records are accepted only if a server already has addresses. Malformed non-memory failures dump the DNS payload for diagnostics.
