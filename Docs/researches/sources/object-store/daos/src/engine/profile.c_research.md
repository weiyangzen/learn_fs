# sources/object-store/daos/src/engine/profile.c

## Purpose
`profile.c` provides a small DAOS server profiling API. It starts and stops per-xstream profiling data collection and associates profile output with the current engine rank and target id.

## Important APIs, Types, and Functions
The file exports `srv_profile_start(char *path, int avg)` and `srv_profile_stop(void)`. It uses `dss_get_module_info()` to access the current `struct dss_module_info`, especially `dmi_dp` for the active `struct daos_profile *` and `dmi_tgt_id` for target attribution.

## Control Flow
`srv_profile_start` gets the current module info, asks CART for the current rank via `crt_group_rank`, then calls `daos_profile_init` with output path, averaging option, rank, and target id. The resulting profile pointer is stored in `dmi->dmi_dp`. `srv_profile_stop` fetches that pointer, dumps profile data, destroys the profile object, and clears `dmi_dp`.

## State and Persistence Behavior
The only local state is the profile pointer stored in per-xstream module info. Profile output is persisted by the profiling library to the supplied path when dumped. There is no guard against starting twice on the same xstream without stopping first, so callers own sequencing.

## Dependencies and Integration Points
The file integrates with CART rank lookup, DAOS profile helpers, server TLS/module info, BIO/SMD includes, and dRPC internals. It is intended to be triggered by server management/profile control paths rather than normal request handling.

## Risks
`srv_profile_stop` assumes `dmi->dmi_dp` is valid; stopping without a successful start could pass NULL to profile helpers depending on their tolerance. Start failure after partial profile allocation depends on `daos_profile_init` cleanup semantics. Rank lookup failure prevents profiling and returns the CART error. Profile paths and averaging settings are not validated here.

## Test Signals
Tests should start and stop profiling on a valid xstream, inject `crt_group_rank` and `daos_profile_init` failures, call stop after start to verify pointer clearing, and exercise management plumbing that requests profile dumps from system and target xstreams.
