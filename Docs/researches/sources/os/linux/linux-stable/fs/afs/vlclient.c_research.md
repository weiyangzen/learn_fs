# File Research: sources/os/linux/linux-stable/fs/afs/vlclient.c

## Scope

Implements AFS and YFS Volume Location Service client RPC marshalling and reply delivery.

## APIs And Behavior

- `afs_vl_get_entry_by_name_u()` calls `VL.GetEntryByNameU`, unmarshalling volume IDs, flags, server UUIDs, server masks, and address versions into `afs_vldb_entry`.
- `afs_vl_get_addrs_u()` calls `VL.GetAddrsU` for a fileserver UUID and returns IPv4 address lists.
- `afs_vl_get_capabilities()` starts async `VL.GetCapabilities` probes used by VL probing.
- `afs_yfsvl_get_endpoints()` calls `YFSVL.GetEndpoints`, parsing IPv4/IPv6 endpoint vectors and ignoring volume endpoints after validating them.
- `afs_yfsvl_get_cell_name()` calls `YFSVL.GetCellName` and returns a bounded NUL-terminated canonical cell name.

## State And Dependencies

Each RPC uses `struct afs_call`, VL cursor peer/address selection, flat-call buffers, XDR structures from `afs_vl.h`, address merge helpers, and call-type deliver/destructor hooks. Probe calls carry VL server/address-list refs until completion.

## Risks And Invariants

Unmarshallers are staged state machines and must reject oversized counts, bad endpoint types, and malformed lengths with protocol errors. UUID byte-order conversion differs between legacy AFS VL structs and YFS opaque UUID payloads.
