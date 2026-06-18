# File Research: sources/os/linux/linux/fs/afs/vlclient.c

## Scope

This file implements AFS and YFS Volume Location Service client RPCs: volume lookup by name, fileserver address lookup, VL capability probes, YFS endpoint lookup, and YFS canonical cell-name lookup.

## Public And Internal APIs Covered

- `afs_vl_get_entry_by_name_u()` dispatches `VL.GetEntryByNameU`.
- `afs_vl_get_addrs_u()` dispatches `VL.GetAddrsU`.
- `afs_vl_get_capabilities()` sends async `VL.GetCapabilities` probes.
- `afs_yfsvl_get_endpoints()` dispatches `YFSVL.GetEndpoints`.
- `afs_yfsvl_get_cell_name()` dispatches `YFSVL.GetCellName`.
- Static deliver functions incrementally unmarshal each reply type.

## Control Flow And Behavior

- `VL.GetEntryByNameU` encodes padded volume names, decodes the UVLDB entry, extracts server UUIDs, server flags, address versions, volume IDs, and volume-type existence bits.
- `VL.GetAddrsU` sends a UUID-based address query and decodes IPv4 address batches into an address list with returned uniquifier as version.
- `VL.GetCapabilities` is async, uses service upgrade, and reports completion through VL probe result hooks.
- `YFSVL.GetEndpoints` decodes counted endpoint lists, validates endpoint count/type/length, merges IPv4/IPv6 fileserver endpoints, and skips volume endpoints after validating their encoding.
- `YFSVL.GetCellName` decodes a bounded padded string and returns an allocated NUL-terminated cell name.
- Each synchronous dispatch records call error, abort code, and responded state back into the VL cursor before releasing the call.

## State And Data Structures

- Uses `struct afs_call` flat request/reply buffers, `ret_vldb`, `ret_alist`, `ret_str`, `vl_probe`, `vlserver`, `probe_index`, and staged `unmarshall` counters.
- Populates `struct afs_vldb_entry` and `struct afs_addr_list`.

## Dependencies

- RxRPC call framework from `rxrpc.c`, XDR structures from AFS/YFS protocol headers, address merge helpers, VL cursor selection state, and probe handling.

## Risks And Invariants

- String and endpoint lengths are protocol-validated before allocation/use.
- YFS endpoint decoding relies on staged extraction because each entry includes the next type/count boundary.
- Async capability calls transfer server/address refs to the call destructor.
