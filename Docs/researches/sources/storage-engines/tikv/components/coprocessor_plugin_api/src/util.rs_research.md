# sources/storage-engines/tikv/components/coprocessor_plugin_api/src/util.rs

Purpose: defines plugin loader symbol names, ABI signatures, build/plugin metadata structs, the `declare_plugin!` macro, and library-name conversion.

Important APIs and types: symbol constants `_plugin_create`, `_plugin_get_build_info`, `_plugin_get_plugin_info`; signatures `PluginConstructorSignature`, `PluginGetBuildInfoSignature`, `PluginGetPluginInfoSignature`; `BuildInfo`, `PluginInfo`, macro `declare_plugin!`, and `pkgname_to_libname`.

Control flow: `declare_plugin!` optionally derives plugin name/version from Cargo env vars, installs `HostAllocator` as global allocator outside tests, exports build-info and plugin-info functions, and exports `_plugin_create`, which sets the host allocator and returns a raw boxed trait object. `BuildInfo::get` reads env vars emitted by `build.rs`.

State and persistence: global allocator state is initialized during plugin creation. Metadata functions return static string references.

Dependencies and integration: central to dynamic loading by TiKV. Uses allocator internals and `CoprocessorPlugin`; host code must look up the exact exported symbols.

Risks: signatures returning Rust structs/trait objects across `extern "C"` are marked with `allow(improper_ctypes_definitions)` and comments note compatibility constraints. Only one plugin can be declared per library because symbols are fixed. `pkgname_to_libname` encodes platform naming assumptions.

Test signals: no direct tests for macro expansion here; allocator test covers one prerequisite. Plugin load tests would be the main validation.
