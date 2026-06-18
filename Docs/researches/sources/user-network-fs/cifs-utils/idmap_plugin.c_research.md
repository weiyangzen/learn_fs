<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmap_plugin.c -->
# sources/user-network-fs/cifs-utils/idmap_plugin.c

## Purpose

`idmap_plugin.c` is the runtime loader and dispatch wrapper for CIFS ID mapping plugins.

## Important APIs, Types, and Functions

Important symbols are global `plugin_errmsg`, static `plugin`, `resolve_symbol`, `open_plugin`, `init_plugin`, `exit_plugin`, `sid_to_str`, `str_to_sid`, `sids_to_ids`, and `ids_to_sids`.

## Control Flow

`init_plugin` opens `IDMAP_PLUGIN_PATH` with `dlopen`, resolves `cifs_idmap_init_plugin`, and calls it to obtain a plugin handle. Each conversion wrapper resolves the corresponding symbol with `dlsym` and dispatches to it, reporting `-ENOSYS` when missing. `exit_plugin` resolves and calls plugin exit if available.

## State and Persistence Behavior

The shared object handle is process-global and left open for program lifetime. The plugin-specific handle is caller-managed. Error text is exposed through global `plugin_errmsg`.

## Dependencies and Integration Points

It depends on `dlopen`/`dlsym`, Autoconf-defined `IDMAP_PLUGIN_PATH`, `cifsidmap.h`, and `idmap_plugin.h`. It is used by `cifs.idmap`, `getcifsacl`, and related ACL utilities.

## Risks and Edge Cases

Function pointer assignment through `*(void **)(&entry)` is a common dlsym workaround but compiler-sensitive. Re-resolving symbols on each call is simple but adds runtime failure points. Global `plugin_errmsg` and `plugin` are not thread-safe, although these helpers are single-process command tools.

## Test Signals

Tests should load a fake plugin, verify every symbol path, missing-symbol errors, plugin init failure, conversion failure messages, and configured path handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/idmap_plugin.c -->
