# sources/user-network-fs/samba/source3/utils/net_registry.c

## Purpose
This file implements the local `net registry` command family for enumerating and editing Samba registry hives, importing/exporting/converting `.reg` files, reading/writing security descriptors, and invoking registry database checks.

## Important APIs, Types, And Control Flow
`open_hive()` splits a path with `split_hive_key()`, creates an admin token, and opens a hive. `open_key()` opens the subkey within that hive. `registry_enumkey()` prints keys and values, optionally recursively. Command functions implement `enumerate`, `enumerate_recursive`, `createkey`, `deletekey`, `deletekey_recursive`, `getvalue`, `getvalueraw`, `getvaluesraw`, `setvalue`, `increment`, `deletevalue`, `getsd`, `getsd_sddl`, `setsd_sddl`, `import`, `export`, `convert`, and `check`. Import uses callback adapters for precheck and actual mutation, wrapped in a regdb transaction. Export recursively emits registry format output through `reg_format`. `net_registry_check()` maps CLI flags into `struct check_options` for `net_registry_check_db()`. `net_registry()` initializes the local registry backend for most commands and dispatches the function table.

## State And Persistence
Most commands directly mutate the local registry database/hives through registry APIs. Import opens regdb, starts a transaction, optionally runs precheck, and commits unless test mode is set. Export and convert write `.reg` files. `increment` serializes DWORD updates with a global `g_lock` key named `registry_increment_lock`.

## Dependencies And Integration Points
Dependencies include registry APIs/backends, registry import/format utilities, admin-token creation, global locks, security descriptor display and SDDL conversion, machine SID lookup, TDB utilities, string conversion, and `net_registry_check.h`/`net_registry_util.h`.

## Risks And Test Signals
The `multi_sz` branch in `net_registry_setvalue()` appears to populate from `argv[count+i]` after `count = argc - 3`, which can include the type string and skip later values; expected indexing is likely from the first value argument. `increment` unlocks only on the success path before cleanup, so error paths rely on context teardown rather than explicit unlock. Local registry edits are destructive, especially recursive delete and import. Test path splitting, recursive enumeration, value set/get for DWORD/SZ/MULTI_SZ, raw output, locked increment failures, SDDL round trips, import precheck/testmode/commit/cancel, export recursion, convert options, registry initialization bypass for `convert` and `check`, and force-delete missing keys.
