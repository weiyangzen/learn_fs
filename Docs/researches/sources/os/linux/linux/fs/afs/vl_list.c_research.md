# File Research: sources/os/linux/linux/fs/afs/vl_list.c

## Scope

This file manages VL server records and lists, including allocation/freeing and parsing DNS server-list payloads into prioritized VL server/address records.

## Public And Internal APIs Covered

- `afs_alloc_vlserver()`, `afs_put_vlserver()`.
- `afs_alloc_vlserver_list()`, `afs_put_vlserverlist()`.
- `afs_extract_vlserver_list()` parses DNS payloads for a cell.
- Internal helpers parse little-endian fields and extract IPv4/IPv6 address lists.

## Control Flow And Behavior

- VL server records are refcounted, named, ported, lock-protected, and initialized with RTT, service ID, probe waitqueue, and address pointer.
- DNS payload parsing validates content type/version, allocates a list sized by header server count, and keeps a reference to the previous list to reuse matching server records.
- Each DNS server entry includes name length, priority, weight, port, source, status, protocol, and address count.
- Only UDP or unspecified protocol is accepted. Port zero defaults to `AFS_VL_PORT`.
- Address extraction accepts IPv4 and IPv6 records, merges them into an `afs_addr_list`, and prefers IPv6 when available.
- Empty address lists are ignored unless the server already has addresses.
- New entries are insertion-sorted by lower priority first, then higher weight.
- Parsing errors dump the DNS buffer except for allocation failure.

## State And Data Structures

- `struct afs_vlserver` stores name, port, addresses, flags, RTT, probe state, and locks.
- `struct afs_vlserver_list` stores refcount, lock, source/status, preferred/index fields, count, and flexible server entries.

## Dependencies

- DNS server-list payload format, address-list allocation/merge helpers, cell `vl_servers_lock`, RCU freeing, and VL probing flags.

## Risks And Invariants

- The parser must always advance through address payloads even when later ignoring an entry.
- Existing server records are reused by case-insensitive name plus port.
- Address pointers are replaced under `server->lock` and old lists are released after replacement.
