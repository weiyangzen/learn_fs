## sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlugin.cc

Purpose: implements runtime plugin loading, symbol lookup, optional preloading, and version compatibility checks.

Important APIs/types/functions: destructor closes `libHandle`; `badVersion()` formats incompatibility messages; `chkVersion()` finds `<pluginSymbol>Version` and applies `XrdVERSIONPLUGINRULES`/`MAXIMS`; `DLflags()` chooses `dlopen` flags; `Find()` searches the preload list; `getLibrary()` opens the shared object or executable image; `getPlugin()` resolves a symbol and reports loaded versions; `Inform()`, `libMsg()`, and `msgSuffix()` route diagnostics; static `Preload()` stores handles in `plList`; `VerCmp()` compares two linked-module versions.

Control flow: `getPlugin()` calls `getLibrary()`, `dlsym()`, `chkVersion()`, then optionally emits a load message. `getLibrary()` reuses object handles or preloaded handles, builds `dlopen` flags, maps `dlerror()` text to `ENOENT`/`ENOEXEC`, and emits errors depending on optionality. Version checking handles no-version, missing-version, dirty/unreleased, bad, and clean outcomes.

State and persistence: each object owns duplicated `libPath` and an optional `dlopen` handle unless `Persist()` detached it. Static `plList` holds preloaded library paths/handles for process lifetime. Diagnostic state points to either `XrdSysError` or caller buffer.

Dependencies and integration: uses POSIX `dlopen`/`dlsym`/`dlclose`, Windows compatibility include, `XrdSysError`, `XrdSysPlatform`, `XrdVersion.hh`, and `XrdVersionPlugin.hh`. Used by plugin-based subsystems including logging and xattr providers.

Risks: preload list is not thread-safe. Version rules depend on symbol naming and copied `XrdVersionInfo` layout. `RTLD_GLOBAL` is unsupported on Windows. `XRDPIHUSH` suppresses non-forced informational messages, which can hide useful client diagnostics.

Test signals: missing library, bad shared object, missing symbol optionality levels, executable-image symbol lookup, preloaded library reuse, `Persist()` lifetime, version clean/missing/bad/unreleased paths, and `XRDPIHUSH` behavior.
