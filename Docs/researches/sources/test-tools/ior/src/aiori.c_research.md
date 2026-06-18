# sources/test-tools/ior/src/aiori.c

## Purpose
Implements the registry and common helpers for IOR's abstract I/O interface. It selects available backends at compile time, exposes option metadata for all modules, provides API listing/default selection, and supplies generic POSIX-based statfs/mkdir/rmdir/access/stat fallbacks.

## Important APIs, Types, And Functions
Defines `available_aiori[]` gated by `USE_*_AIORI` macros. Exports `airoi_create_all_module_options`, `airoi_update_module_options`, `aiori_supported_apis`, `aiori_posix_statfs`, `aiori_posix_mkdir`, `aiori_posix_rmdir`, `aiori_posix_access`, `aiori_posix_stat`, `aiori_get_version`, `aiori_select`, `aiori_count`, and `aiori_default`.

## Control Flow
At startup or option parsing, callers can create a module option set for every compiled backend. `aiori_select` scans the registry for the requested canonical or legacy name, warns on legacy use, fills missing metadata hooks with POSIX fallbacks, and returns the backend function table. Supported API strings are built by iterating the registry and optionally filtering for mdtest-enabled backends.

## State And Persistence Behavior
The registry is static process state. `aiori_select` mutates backend function tables by installing fallback function pointers the first time a backend is selected. POSIX statfs derives the parent directory from a duplicated path and translates platform statfs/statvfs fields into `ior_aiori_statfs_t`.

## Dependencies And Integration Points
Depends on compile-time backend symbols declared in `aiori.h`, option structures from `option.h`, POSIX/statvfs or statfs headers, and debug warnings. It is used by command-line parsing and `init_IOR_Param_t`/`ValidateTests` in `ior.c`.

## Risks And Edge Cases
`airoi_update_module_options` indexes modules by walking both `available_aiori` and `opt->modules`; mismatched ordering would update the wrong module. Fallback mutation of global backend tables is convenient but can hide missing backend operations. `aiori_posix_statfs` returns early on statfs failure without freeing `fileName`. It sets `f_bavail` only in the `ior_aiori_statfs_t` struct definition, but this helper does not copy it. `aiori_default` can return `dummy_aiori` if it is the first compiled entry after unavailable optional backends.

## Test Signals
Compile matrices with different `USE_*_AIORI` macros, `-a` selection by canonical and legacy names, mdtest API listing, option help generation, and fallback stat/mkdir/access behavior for a backend with missing hooks are primary tests.
