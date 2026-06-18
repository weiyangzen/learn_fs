# sources/user-network-fs/samba/source3/registry/reg_backend_perflib.c

## Purpose
`reg_backend_perflib.c` implements a virtual registry backend for the Windows performance library keys. It synthesizes values for `HKLM\SOFTWARE\MICROSOFT\WINDOWS NT\CURRENTVERSION\PERFLIB` and the English `...\PERFLIB\009` child rather than storing those values directly in `registry.tdb`.

## Important APIs, Types, And Functions
The exported integration point is `struct registry_ops perflib_reg_ops`, with `.fetch_values` and `.fetch_subkeys`. `perflib_params()` adds `Base Index`, `Last Counter`, `Last Help`, and `Version` as `REG_DWORD` values using `reg_perfcount_get_base_index()`, `reg_perfcount_get_last_counter()`, and `reg_perfcount_get_last_help()`. `perflib_009_params()` adds `Counter` and `Help` as `REG_MULTI_SZ` buffers returned by `reg_perfcount_get_counter_names()` and `reg_perfcount_get_counter_help()`.

## Control Flow
`perflib_fetch_values()` duplicates and normalizes the requested key, then dispatches to one of the two value producers. Subkey enumeration is not virtualized; `perflib_fetch_subkeys()` delegates to `regdb_ops.fetch_subkeys()`, so stored database children remain visible under the dynamic path.

## State And Persistence
No values are persisted by this backend. Value contents are computed from the performance counter subsystem on each fetch. Temporary buffers from performance counter helpers are released with `SAFE_FREE()` when a positive buffer size is returned.

## Dependencies And Integration Points
The backend depends on `registry.h`, `reg_util_internal.h`, `reg_perfcount.h`, `reg_objects.h`, and the default `regdb_ops`. It is registered under `KEY_PERFLIB` by `reg_init_full.c`, after which the hook cache routes matching key handles through `perflib_reg_ops`.

## Risks And Test Signals
The path checks use `strncmp(path, KEY, strlen(path))`, which treats shorter prefixes as matches and should be exercised with exact key names, the `009` child, and malformed/partial paths. Tests should verify DWORD byte sizes, correct `REG_MULTI_SZ` payloads, empty counter helper behavior, and continued delegation of subkey enumeration to the registry database.
