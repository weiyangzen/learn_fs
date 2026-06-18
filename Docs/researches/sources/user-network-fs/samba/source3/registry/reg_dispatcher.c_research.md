# sources/user-network-fs/samba/source3/registry/reg_dispatcher.c

## Purpose
`reg_dispatcher.c` provides frontend wrapper functions that call the selected registry backend operations for an open key handle. It also supplies default registry security descriptor behavior when a backend does not implement its own.

## Important APIs, Types, And Functions
The public functions mirror `registry_ops`: `store_reg_keys()`, `store_reg_values()`, `create_reg_subkey()`, `delete_reg_subkey()`, `fetch_reg_keys()`, `fetch_reg_values()`, `regkey_access_check()`, `regkey_get_secdesc()`, `regkey_set_secdesc()`, `reg_subkeys_need_update()`, and `reg_values_need_update()`. `construct_registry_sd()` builds the fallback security descriptor with read access for Everyone and full access for Builtin Administrators and System. `reg_generic_map` maps generic access to registry-specific rights.

## Control Flow
Most wrappers check `key->ops` and the relevant function pointer, call it if present, and otherwise return `false`, `-1`, `WERR_NOT_SUPPORTED`, or `WERR_ACCESS_DENIED`. `regkey_access_check()` gives root mode a full-access bypass, uses backend-specific access checks when present, otherwise gets a security descriptor, maps generic bits, and calls `se_access_check()`.

## State And Persistence
This file does not persist state. It is a dispatch layer over backend state and builds temporary security descriptors under the caller's talloc context. Freshness checks default to `true`, forcing callers to refresh if a backend does not provide sequence-aware logic.

## Dependencies And Integration Points
It depends on `registry.h`, `reg_dispatcher.h`, `system/passwd.h` for root-mode support, and Samba security helpers. Registry frontend code calls these wrappers after `reghook_cache_find()` has placed an ops pointer in `struct registry_key_handle`.

## Risks And Test Signals
Default security behavior is security-sensitive. Tests should cover root bypass, backend override, fallback descriptor ACEs, generic access mapping, denied requests, and failure to read backend security descriptors falling back only when appropriate. Wrapper tests should verify each missing callback returns the documented default and that update checks default to refresh-needed.
