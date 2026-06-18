# sources/test-tools/ior/src/aiori.h

## Purpose
Defines IOR's abstract I/O interface contract. It gives core benchmark code a uniform function table for different storage backends and declares backend selection, option, version, and POSIX fallback helpers.

## Important APIs, Types, And Functions
Defines IOR open/mode flags, `ior_aiori_statfs_t`, `aiori_xfer_hint_t`, opaque `aiori_mod_opt_t`, opaque `aiori_fd_t`, and the central `ior_aiori_t` function table. Declares all backend instances, `aiori_select`, `aiori_count`, `aiori_supported_apis`, `airoi_create_all_module_options`, `airoi_update_module_options`, `aiori_default`, generic POSIX helper functions, and reusable MPIIO option/API declarations.

## Control Flow
Backends fill `ior_aiori_t` hooks for create/open/xfer/close/remove/get_file_size/stat/metadata/initialize/finalize/options/check/sync. `ior.c` selects one backend, sends transfer hints, and then calls these hooks through the test lifecycle. Optional hooks may be filled by `aiori.c` fallbacks.

## State And Persistence Behavior
The header owns no state. `aiori_xfer_hint_t` is the state-transfer structure from `IOR_param_t` to backends, carrying access pattern, sizes, aggregate expectations, fsync flags, and dry-run/single-xfer hints.

## Dependencies And Integration Points
Includes `iordef.h`, `aiori-debug.h`, `option.h`, stat definitions, and bool. It is included by core IOR, mdtest-aware backend code, and backend implementations. The `enable_mdtest` field is the integration switch for mdtest API listings.

## Risks And Edge Cases
The interface uses opaque structs that are cast to backend-specific types, so type safety is minimal. Many hooks are allowed to be NULL and later defaulted, which can surprise non-POSIX backends. Changing `mpiio_options_t` requires synchronized changes in dependent modules. The `xfer` contract returns bytes transferred, and backend violations directly affect IOR validation.

## Test Signals
ABI/compiler checks across all enabled backends, backend selection smoke tests, transfer-hint propagation tests, and mdtest API filtering validate this contract.
