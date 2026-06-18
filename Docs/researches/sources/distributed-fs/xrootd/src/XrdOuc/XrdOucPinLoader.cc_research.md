<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.cc

Purpose: Implements version-aware shared-library plugin loading and symbol resolution.

APIs and control flow: Constructors initialize error routing via `XrdSysError`, caller-provided buffer, or allocated buffer. `Init()` warns about version syntax in paths, computes a primary versioned library path through `XrdOucVerName::Version()`, and records an unversioned fallback when allowed. `Resolve()` validates load state, lazy-loads via `LoadLib()`, handles optional `?`/`!` symbol prefixes, and calls `XrdSysPlugin::getPlugin()`. `LoadLib()` tries the versioned library, falls back on not-found cases, and tracks bad-library state. `Unload()` drops the plugin object.

State and persistence: Owns `theLib`, `altLib`, optional error buffer, and `XrdSysPlugin`. The destructor persists loaded plugin images unless `Unload()` removed the plugin object.

Dependencies and integration: Wraps `XrdSysPlugin`, `XrdOucVerName`, XRootD version metadata, and server/client diagnostics.

Risks and test signals: Fallback behavior depends on `errno` from plugin loading. Tests should cover versioned path generation, alternate fallback, optional symbols, buffer diagnostics, global symbol mode, explicit unload, and destructor persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinLoader.cc -->
