# sources/object-store/daos/src/engine/module.c

## Purpose
`module.c` implements the server-side dynamic module framework. It loads DAOS module shared libraries, resolves their exported `struct dss_module`, registers module TLS keys, RPC handlers, dRPC handlers, metrics hooks, setup/cleanup callbacks, and unloads modules during shutdown.

## Important APIs, Types, and Functions
`struct loaded_mod` tracks a `dlopen` handle, module interface pointer, list link, and init flag. Public functions include `dss_module_get`, `dss_module_load`, `dss_module_init_all`, `dss_module_unload`, `dss_module_setup_all`, `dss_module_cleanup_all`, `dss_module_init`, `dss_module_fini`, `dss_module_unload_all`, `dss_module_init_metrics`, `dss_module_fini_metrics`, and `dss_module_nr_pool_metrics`. `dss_modules[DAOS_MAX_MODULE]` provides fast module lookup by module id.

## Control Flow
`dss_module_load` validates the short module name, opens `lib<name>.so`, resolves `<name>_module`, checks `sm_name`, then links it into `loaded_mod_list`. `dss_module_init_all` walks the load order and calls `dss_module_init_one`, which invokes `sm_init`, registers TLS keys, DAOS RPC protocol handlers, dRPC handlers, and returns module facility bits. Cleanup paths unregister RPC and dRPC handlers, unregister keys, call `sm_fini`, close libraries, and free tracking objects. Setup runs in load order; cleanup runs reverse order.

## State and Persistence Behavior
Module state is in-process only: the loaded module list, `dss_modules` lookup array, and any module-owned state initialized behind `sm_init` or setup hooks. The framework does not persist data directly, but loaded modules such as VOS/pool/container may open persistent state as part of their own callbacks.

## Dependencies and Integration Points
This file depends on `dlopen`/`dlsym`/`dlclose`, GURT lists, DAOS RPC registration, dRPC handler registration, module TLS key registration, and telemetry metrics initialization. It is invoked from `init.c` around CART startup and from service setup/cleanup paths.

## Risks
The module list is protected by a pthread mutex for structural updates, but metrics helpers iterate without taking the lock; this assumes stable module lifetime after startup. `dss_module_init_one` removes and frees a module on init failure while `dss_module_init_all` is iterating, so error paths must remain list-safe. A module id outside `DAOS_MAX_MODULE`, duplicate id, or inconsistent name can corrupt dispatch expectations. Partial registration failures must unregister only what was already registered.

## Test Signals
Tests should cover successful and failed `dlopen`, missing symbol, mismatched module name, RPC/dRPC registration failures, reverse cleanup order, repeated unload of missing modules, metrics init/fini for SYS/TGT tags, and module lookup for CART-originated pseudo module ids above `DAOS_MAX_MODULE`.
