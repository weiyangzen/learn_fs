# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kidmap.h

## Purpose
Defines the kernel API for mapping Windows SIDs to Solaris UIDs/GIDs and back, including single-request and batched lookup flows.

## Main Interfaces
- `idmap_get_handle_t`: opaque batch lookup handle.
- `idmap_stat`: 32-bit status type.
- Direct lookups:
  - `kidmap_getuidbysid()`
  - `kidmap_getgidbysid()`
  - `kidmap_getpidbysid()`
  - `kidmap_getsidbyuid()`
  - `kidmap_getsidbygid()`
- Batch lifecycle:
  - `kidmap_get_create()`
  - `kidmap_batch_get*()`
  - `kidmap_get_mappings()`
  - `kidmap_get_destroy()`
- Door/cache support:
  - `idmap_reg_dh()`
  - `idmap_unreg_dh()`
  - `idmap_get_door()`
  - `idmap_purge_cache()`

## Dependencies And Relationships
Includes `sys/idmap.h`, `sys/door.h`, and `sys/zone.h`. Every mapping call is zone-aware via `zone_t *`, and daemon communication is represented through door handles.

## Research Notes
The SID representation is split into a string SID prefix and integer RID. Returned SID prefix pointers refer to internal storage and must not be modified or freed by callers.
