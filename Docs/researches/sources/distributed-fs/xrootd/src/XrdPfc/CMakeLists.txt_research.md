<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdPfc/CMakeLists.txt

## Purpose

`XrdPfc/CMakeLists.txt` builds and installs the proxy file cache plugin, the blacklist decision plugin, the purge quota plugin, and the `xrdpfc_print` inspection tool.

## Important APIs, Types, And Functions

- Defines module targets `${XrdBlacklistDecision}`, `${XrdPfc}`, and `${XrdPfcPurgeQuota}` with `${PLUGIN_VERSION}` suffixes.
- Builds `${XrdPfc}` from core cache, configuration, command, directory-state, purge, file, IO, info, traversal, and resource monitor sources.
- Installs public PFC headers under `${CMAKE_INSTALL_INCLUDEDIR}/xrootd/XrdPfc`.
- Links `${XrdPfc}` with `XrdCl`, `XrdUtils`, `XrdServer`, and `XrdPosix`.
- Installs a compatibility symlink from `libXrdFileCache.so` to the versioned `libXrdPfc` module.
- Builds `xrdpfc_print` from info/print sources for reading cache metadata.

## Control Flow

The build file declares plugins first, then install rules for headers and libraries, then a post-install symlink action, then the standalone print executable. Source list membership controls what participates in the runtime cache module.

## State And Persistence

CMake produces installed shared libraries, headers, the compatibility symlink, and the `xrdpfc_print` binary. No runtime state is affected directly.

## Dependencies And Integration Points

The target integrates XrdPfc into the XRootD plugin system through module libraries and exported headers. The symlink preserves older `XrdFileCache` naming for deployments or configs that still use it.

## Risks And Edge Cases

- The install-time `ln -sf` assumes a Unix-like environment and a library name prefix of `lib`.
- Public header installation must stay aligned with headers included by external purge/decision tooling.
- Adding source files without updating this list can silently omit implementation from the plugin module.

## Test Signals

Build tests should verify all three modules build, `xrdpfc_print` links, headers install, and the compatibility symlink points to the versioned PFC module in staged installs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/CMakeLists.txt -->
