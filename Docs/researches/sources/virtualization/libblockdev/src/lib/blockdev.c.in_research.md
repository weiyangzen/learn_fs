# File Research: sources/virtualization/libblockdev/src/lib/blockdev.c.in

## Role
Template for the main libblockdev loader implementation. It initializes logging, reads plugin configuration, dynamically loads and unloads plugin shared objects, tracks loaded plugin state, and exposes public initialization/query APIs.

## Structure
- Includes `dlfcn.h`, libblockdev utilities, public core headers, and every generated plugin API wrapper C/H pair.
- S390 plugin wrappers are included only on `__s390__` or `__s390x__`.
- Defines the default config directory as `/etc/libblockdev/@MAJOR_VER@/conf.d/`.
- Maintains global state through `init_lock`, `initialized`, and a static `plugins[BD_PLUGIN_UNDEF]` table of `BDPluginStatus`.
- Keeps three order-sensitive arrays aligned with the `BDPlugin` enum:
  - default shared object names, such as `libbd_lvm.so.@MAJOR_VER@` and `libbd_btrfs.so.@MAJOR_VER@`;
  - plugin handle/spec state;
  - human-readable plugin names.

## Configuration Loading
- `get_config_files()` chooses `LIBBLOCKDEV_CONFIG_DIR` if set, otherwise the default config path.
- Only `.cfg` files are included, and they are sorted lexicographically with `GSequence`.
- `process_config_file()` reads a `sonames` string list per plugin section, preserving configured order despite prepending into GSLists.
- `load_config()` processes config files sequentially and logs/skips malformed files instead of aborting all initialization.
- Missing plugin soname lists are filled with built-in defaults.
- On non-s390 architectures, the S390 plugin default is explicitly removed unless requested.

## Plugin Loading and Unloading
- `unload_plugins()` calls each generated `unload_<plugin>()` wrapper for loaded handles, logging warnings on close failure.
- `load_plugin_from_sonames()` tries configured sonames until one loads, then stores the loaded soname in plugin state.
- `do_load()` dispatches each plugin to its generated `load_<plugin>_from_plugin()` wrapper.
- `load_plugins()` is the central policy function:
  - loads config and defaults;
  - optionally unloads/reloads existing plugins and clears stored sonames;
  - restricts load attempts to explicitly required plugins when `require_plugins` is non-NULL;
  - lets requested specs override default/configured sonames;
  - counts successfully loaded requested/default plugins;
  - returns whether all requested/default plugins loaded.

## Public Initialization API
- `bd_init()` initializes once, sets up logging if provided, loads all or required plugins, and treats missing requested/default plugins as `BD_INIT_ERROR_PLUGINS_FAILED`.
- `bd_ensure_init()` performs an atomic check-and-init/reinit under `init_lock`; if already initialized, it checks whether requested plugins are available before returning early.
- `bd_try_init()` is tolerant of plugin load failures: it returns the `load_plugins()` success state but documents that failure to load a plugin is not considered an error; it can also return loaded plugin names.
- `bd_reinit()` reloads or adds missing plugins. A NULL-first required-plugin array plus `reload=TRUE` is treated as an explicit unload-all request.
- `bd_try_reinit()` mirrors `bd_reinit()` with tolerant plugin-load semantics and optional loaded plugin names.
- `bd_is_initialized()` returns the locked global initialization state.

## Public Query API
- `bd_get_available_plugin_names()` returns a NULL-terminated array container of names for plugins with non-NULL handles. The strings themselves are static.
- `bd_is_plugin_available()` checks handle presence for a valid enum value.
- `bd_get_plugin_soname()` returns a newly duplicated loaded soname or NULL.
- `bd_get_plugin_name()` returns the static plugin name for a valid enum value.

## Error and Concurrency Behavior
- Initialization and reinitialization are serialized with `init_lock`.
- Dependency/plugin load failures are accumulated as boolean success plus GLib `GError`.
- Config directory open failure logs fallback to built-in config.
- Config file parse failures are warnings and do not stop later files.

## Filesystem/Storage Relevance
This file is the runtime switchboard that makes filesystem and block-device operations available through dynamically loaded plugins. For Btrfs, FS, LVM, DM, mdraid, NVMe, and related storage plugins, availability depends on this file successfully resolving plugin sonames and handles.
