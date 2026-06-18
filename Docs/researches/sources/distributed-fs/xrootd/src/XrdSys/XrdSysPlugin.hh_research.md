# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPlugin.hh

Purpose: declares `XrdSysPlugin`, XRootD's utility for loading runtime plugin shared libraries, resolving exported C symbols, optionally comparing plugin and caller version metadata, and controlling library lifetime.

Important APIs/types/functions: public entry points are `getLibrary()`, both `getPlugin()` overloads, `Persist()`, static `Preload()`, and static `VerCmp()`. Constructors support three error-routing modes: no version checking, version checking with `XrdSysError`, and version checking with a caller-supplied error buffer. Private helpers such as `chkVersion()`, `badVersion()`, `DLflags()`, `Find()`, `Inform()`, `libMsg()`, and `msgSuffix()` are implemented in `XrdSysPlugin.cc`. `PLlist` tracks preloaded libraries.

Control flow: callers construct the loader with a library path or null path for the executable image, then call `getPlugin()`. `getPlugin()` implicitly opens the library through `getLibrary()`, finds the requested symbol, optionally finds the `<symbol>Version` companion, and validates compatibility when `myInfo` is present. `Persist()` transfers ownership of the loaded handle by clearing `libHandle`, causing the destructor not to close it.

State and persistence: each instance owns `libPath` storage created by `strdup`, a transient `libHandle`, optional logical name and version pointer, and either an error route or buffer. The static `plList` persists preloaded handles process-wide. `Persist()` intentionally leaks the library handle to the caller/process lifetime.

Dependencies and integration: depends on `XrdVersionInfo` naming conventions from `XrdVersion.hh`, `XrdSysError` for diagnostics, and POSIX dynamic loader behavior implemented in the `.cc`. It is used by plugin stacks such as XrdThrottle to load alternate file system modules.

Risks: the header documents that `Preload()` is not thread-safe and should run before threads start. `Persist()` can cause a later `getPlugin()` on the same object to reopen the library. Version checking depends on plugin authors exporting the exact symbol name with `Version` appended. Constructor comments require path/name storage to persist, but `path` is copied while `lname` is not, so callers must keep `lname` valid.

Test signals: useful checks include loading an existing plugin, missing-library and missing-symbol error paths, optional symbol suppression, `Persist()` lifetime behavior, preload lookup, and clean/dirty version combinations.
