# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/damap.h

Public Delta Address Map API. It provides stabilized string-address sets for device/bus discovery, supporting per-address reports, full-set reports, delayed stabilization, activation/release callbacks, configure/unconfigure callouts, lookup, and reference management.

Key elements:
- Opening comment explains per-address reporting, full-set reporting, stabilization timers, activation/release, and stable-address lookup.
- Defines opaque `damap_t`, `damap_id_t`, and unused `damap_id_list_t`; `NODAM` is the null ID.
- Deactivation reasons distinguish gone, configuration failure, and unstable report.
- Provider callbacks handle address activation and deactivation with provider-private state.
- Class callbacks handle configuration and unconfiguration of stabilized addresses.
- Report modes are per-address and full-set.
- Map options distinguish serialized configuration and multithreaded configuration.
- `damap_create()` wires map name, report mode, stabilization/config parameters, callback arguments, callbacks, and returned map handle.
- Basic APIs destroy maps, query name/size/empty state, and synchronize with pending operations.
- Per-address APIs add/delete by string or ID.
- Full-set APIs begin/add/end, flush, and reset address sets; `DAMAP_END_RESET` and `DAMAP_END_ABORT` modify end behavior.
- Lookup/reference APIs iterate IDs, map ID to address/nvlist/private data, hold/release/ref IDs, set/get private data, lookup one address, and lookup all stable addresses.
- Return codes include success, exists, map full, invalid, generic failure, and `DAM_SHAME`.

Dependencies:
- Uses `nvlist_t` payloads and kernel callback patterns; concrete structures are private in `damap_impl.h`.
- Intended for bus/device discovery layers that need debounce/stabilization before configuring devices.

Research notes:
- Full-set reporting frees providers from issuing explicit deletes for disappeared addresses; stabilization applies to the entire reported set.
- IDs require explicit hold/release in lookup paths to avoid use-after-release while configuration/unconfiguration proceeds.
