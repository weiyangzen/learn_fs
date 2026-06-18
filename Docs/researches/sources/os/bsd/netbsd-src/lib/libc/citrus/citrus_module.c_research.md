# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_module.c

Dynamic i18n module loader for Citrus.

Key behavior:
- When `_I18N_DYNAMIC` is enabled, locates shared libraries named `lib<encname>.so.<major>[.<minor>]` in the i18n module directory.
- Determines search directory from `PATH_I18NMODULE` unless setugid, otherwise uses `_PATH_I18NMODULE`, with optional `MLIBDIR` rewriting.
- Parses and compares Dewey-style shared-library version suffixes.
- `_citrus_load_module` finds a compatible module with `I18NMODULE_MAJOR` and opens it with `dlopen`.
- `_citrus_find_getops` builds the symbol name `_citrus_<modname>_<ifname>_getops` and resolves it with `dlsym`.
- `_citrus_unload_module` calls `dlclose`.
- In non-dynamic builds, loading and getops lookup return failure/no-op.

Security/compatibility:
- Ignores environment override in setugid programs.
- Has a special m68k stack protector optimization attribute workaround.
