# sources/storage-engines/tikv/src/coprocessor_v2/plugin_registry.rs

## Purpose
Loads, indexes, hot-reloads, and exposes dynamic coprocessor plugin libraries. It validates plugin ABI/build compatibility before constructing plugin instances.

## Important APIs, Types, and Functions
`PluginLoadingError` distinguishes dylib load failures, semver parse errors, rustc/target/API mismatches, and reload attempts. `PluginRegistry` wraps `Arc<RwLock<PluginRegistryInner>>` plus an optional filesystem watcher. Public methods load/unload plugins, start hot reloading, query by name/path, update paths, and list names. `PluginRegistryInner` stores `loaded_plugins: HashMap<String, (OsString, Arc<LoadedPlugin>)>` and `library_paths: HashSet<OsString>`. `LoadedPlugin::new` loads symbols, validates `BuildInfo`, constructs the plugin through `PLUGIN_CONSTRUCTOR_SYMBOL`, and intentionally leaks the `Library`. `LoadedPlugin` implements `CoprocessorPlugin` by delegation.

## Control Flow
`start_hot_reloading` creates the directory, starts one notify watcher thread if needed, registers the directory, and preloads existing library files. Create events attempt load; remove/write events warn that already-loaded code remains running; rename events update the stored path. `load_plugin` rejects any exact path previously loaded, constructs `LoadedPlugin`, records the path permanently in `library_paths`, and indexes by plugin name.

## State and Persistence Behavior
Registry state is in memory. Dynamic libraries are intentionally never unloaded from process memory because Rust/dylib plugin safety requires stable code and vtables. Unloading removes the name mapping but the path remains in `library_paths`, preventing reload from the same exact path. Filesystem state is watched but not authoritatively reconciled after deletion/overwrite.

## Dependencies and Integration Points
Depends on `libloading`, `notify`, `semver`, and `coprocessor_plugin_api` ABI symbols. `Endpoint` calls `get_plugin` for request dispatch. The plugin directory is configured by `coprocessor_v2::Config`.

## Risks and Edge Cases
Unsafe dynamic loading is central: symbol signatures and plugin ABI must match. Leaking libraries avoids unload hazards but means long-running processes retain code and memory. Path identity is exact and not canonicalized, so `./x.so` and `x.so` differ. Hot reload ignores load errors and cannot replace a loaded plugin on write/delete, which is operationally important. Duplicate plugin names overwrite previous loaded name entries while old library code remains leaked.

## Test Signals
Tests load the example plugin, verify registry lookup/path listing, path update, unload behavior, and hot-reload create/rename/remove behavior with sleeps for debounced notify. Tests do not cover duplicate names, relative path aliases, API mismatch, or semver parse failure in plugin metadata.
