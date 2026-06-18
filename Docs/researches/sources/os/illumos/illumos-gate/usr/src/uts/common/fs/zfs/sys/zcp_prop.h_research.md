# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_prop.h

This header declares channel-program property getter support and dataset-property validation.

Public API surface:
- `zcp_load_get_lib(lua_State *)` loads property-get functions into a Lua state.
- `prop_valid_for_ds(dsl_dataset_t *, zfs_prop_t)` checks whether a ZFS property is valid for a specific dataset.

Risk-sensitive invariants:
- Property validity is dataset-dependent and must be checked before exposing or using property operations in scripts.
- The header assumes the including context provides the relevant DSL dataset and ZFS property type definitions.
