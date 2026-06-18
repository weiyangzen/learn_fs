# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/overlay_plugin.h

## Purpose
Defines the private illumos overlay encapsulation/decapsulation plugin interface used by kernel modules that implement formats such as VXLAN, NVGRE, or Geneve.

## Main Interfaces
- `OVEP_VERSION`: current plugin ABI version.
- `overlay_plugin_flags_t`: plugin feature flags, currently `OVEP_F_VLAN_TAG`.
- `ovep_encap_info_t`: overlay packet metadata containing virtual network identifier and header size.
- Opaque handles:
  - `overlay_prop_handle_t`
  - `overlay_handle_t`
- Plugin callbacks:
  - `overlay_plugin_init_t`, `overlay_plugin_fini_t`
  - `overlay_plugin_encap_t`, `overlay_plugin_decap_t`
  - `overlay_plugin_socket_t`, `overlay_plugin_sockopt_t`
  - `overlay_plugin_getprop_t`, `overlay_plugin_setprop_t`
  - `overlay_plugin_propinfo_t`
- `overlay_plugin_ops_t`: operation vector installed by a plugin.
- `overlay_plugin_register_t`: registration record with version, name, ops, property names, ID width, flags, and destination requirements.
- Registration API:
  - `overlay_plugin_alloc()`
  - `overlay_plugin_free()`
  - `overlay_plugin_register()`
  - `overlay_plugin_unregister()`
- Property-description helpers:
  - `overlay_prop_set_name()`
  - `overlay_prop_set_prot()`
  - `overlay_prop_set_type()`
  - `overlay_prop_set_default()`
  - `overlay_prop_set_nodefault()`
  - `overlay_prop_set_range_uint32()`
  - `overlay_prop_set_range_str()`

## Dependencies And Relationships
Includes STREAMS message blocks, MAC provider definitions, kernel sockets, and `overlay_common.h`. It is consumed by overlay format modules and the broader overlay device framework.

## Research Notes
The header documents module lifecycle ordering: register before `mod_install()`, unregister on failed install or `_fini()`, and refuse unload while busy. It also states synchronization rules: instances may be called concurrently, `getprop`/`setprop` are MAC-perimeter serialized, and encap/decap may run in interrupt context below `LOCK_LEVEL`.
