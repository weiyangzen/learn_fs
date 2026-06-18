<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.cc

Purpose: Implements a public utility wrapper for computing versioned plugin library paths.

APIs and control flow: `XrdOucPinPath()` delegates to `XrdOucVerName::Version()` with `XRDPLUGIN_SOVERSION`, filling the caller buffer and setting `noAltP` to indicate whether fallback to the original path is allowed.

State and persistence: Stateless; it writes only to caller-provided output parameters.

Dependencies and integration: Integrates public plugin path users with the same version naming logic used by `XrdOucPinLoader`.

Risks and test signals: Buffer size is the main failure mode. Tests should compare output against loader path selection, include paths with and without existing version suffixes, and verify `noAltP` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.cc -->
