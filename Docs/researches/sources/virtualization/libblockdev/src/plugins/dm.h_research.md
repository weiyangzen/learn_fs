# File Research: sources/virtualization/libblockdev/src/plugins/dm.h

## Role

`dm.h` is the public header for libblockdev's device-mapper plugin.

## Public API

It declares:

- `BDDMError` values for unavailable tech, sys errors, root requirement, task errors, RAID-related errors, and missing device errors.
- `BDDMTech`, currently only `BD_DM_TECH_MAP`.
- `BDDMTechMode` for create/activate, remove/deactivate, and query.
- plugin lifecycle functions `bd_dm_init()` and `bd_dm_close()`.
- technology availability checking.
- map operations: create linear map, remove map, check map existence, map name from dm node, dm node from map name, subsystem from dm name.

## Dependencies

The header only includes GLib and exposes no libdevmapper types. This keeps the public ABI independent of libdevmapper structs.

## Notable Risks

The enum contains RAID error values even though this implementation only handles map operations, suggesting historical or shared ABI baggage.
