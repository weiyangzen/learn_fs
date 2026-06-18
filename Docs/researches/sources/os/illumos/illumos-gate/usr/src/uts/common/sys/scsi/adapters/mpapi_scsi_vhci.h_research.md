# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpapi_scsi_vhci.h

## Purpose
Defines private `scsi_vhci` MPAPI bookkeeping structures: object IDs, generic item/list containers, and per-object cached data used to expose initiator ports, logical units, paths, target port groups, and target ports through the MPAPI ioctl layer.

## Main Interfaces
- Object ID representation:
  - `mp_oid_t` splits a 64-bit ID into timestamp, object type, and sequence ID with endian-aware bitfield ordering.
  - `mpoid_t` exposes the same ID as either raw `uint64_t` or decoded `mp_oid_t`.
- Generic list/item containers:
  - `mpapi_item_t` stores an OID, object-private data pointer, and mutex.
  - `mpapi_item_list_t` links items.
  - `mpapi_list_header_t` tracks head and tail.
- Cached object data:
  - `mpapi_initiator_data_t`
  - `mpapi_lu_data_t`
  - `mpapi_path_data_t`
  - `mpapi_tpg_data_t`
  - `mpapi_tport_data_t`
- Global MPAPI private state:
  - `mpapi_priv_t` stores a timestamp for stale-OID detection, per-object-type sequence counters, and one object-list header per `MP_OBJECT_TYPE_*`.

## Dependencies And Relationships
Includes `sys/scsi/adapters/mpapi_impl.h`, so all cached property structs are the ABI records from `mpapi_impl.h`. The comments refer to MDI pathinfo state, destroyed paths, standby/online path validity, and `scsi_vhci` virtual LU/path objects.

## Research Notes
`MPAPI_SCSI_MAXPCLASSLEN` fixes the path-class buffer at 25 bytes. Path and TPG data both cache a path class string, validity, and property snapshots. `mpapi_path_data_t` has separate `valid` and `hide` flags: `hide` is used when a path was destroyed or should have been destroyed, and forces invalid visibility.

## Notable Risks
- `mp_oid_t` uses C bitfields and therefore requires `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`; endian handling is part of the object-ID ABI.
- List and item structures carry mutex-protected mutable state, so object removal and stale-OID detection must stay synchronized with MDI path lifecycle changes.
- The sequence counter array is indexed by MP object type; object-type constants from `mpapi_impl.h` must stay within `MP_MAX_OBJECT_TYPE`.
