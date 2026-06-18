# sources/user-network-fs/samba/source3/smbd/mangle.c

## Purpose
`mangle.c` is the dispatch layer for Samba's DOS 8.3 name mangling subsystem. It selects a backend based on `mangling method`, exposes wrapper APIs used by directory/path code, and provides a POSIX-mode switch that disables mangling behavior.

## Important APIs, Types, And Functions
`mangle_backends[]` maps backend names to initialization functions: `hash`, `hash2`, and `posix`. `mangle_init()` lazily chooses the configured backend and terminates the server if no backend initializes. Public wrappers are `mangle_reset_cache()`, `mangle_change_to_posix()`, `mangle_is_mangled()`, `mangle_is_8_3()`, `mangle_is_8_3_wildcards()`, `mangle_must_mangle()`, `mangle_lookup_name_from_8_3()`, and `name_to_8_3()`.

## Control Flow
Most wrappers assume `mangle_fns` is initialized by startup or by a prior reset; `mangle_reset_cache()` explicitly calls `mangle_init()` before invoking the backend reset hook. `mangle_change_to_posix()` clears the current backend, sets the loadparm mangling method to `posix`, and reinitializes. `name_to_8_3()` returns a simple truncation when mangled names are disabled for the share; otherwise it delegates to the selected backend with share default-case settings.

## State And Persistence
The selected backend is the global function table `mangle_fns`. Backend caches live in `mangle_hash.c` or `mangle_hash2.c`; this file only selects and calls them. The POSIX switch mutates runtime configuration through `lp_set_mangling_method("posix")`.

## Dependencies And Integration Points
This file integrates with loadparm (`lp_mangling_method`, `lp_mangled_names`, `lp_default_case`), global mangling state in `globals.c`, and `struct mangle_fns` from `mangle.h`. `filename.c` and directory enumeration use these wrappers for mangled-name detection, reverse lookup, and 8.3 output generation.

## Risks
Several wrappers dereference `mangle_fns` without calling `mangle_init()`, so initialization ordering matters. Runtime switching to POSIX mangling affects all later name resolution in the process. Disabling mangled names truncates rather than hashes, which can create collisions or client-visible ambiguity.

## Test Signals
Tests should cover backend selection by parameter, default fallback, failure-to-initialize exit behavior, cache reset, POSIX switch, mangled-names disabled truncation, wildcard 8.3 checks, and wrapper behavior across `hash`, `hash2`, and `posix` backends.
