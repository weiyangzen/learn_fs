<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.cc

Purpose: Implements plugin preloading so a shared library image can be loaded and persisted before later plugin initialization.

APIs and control flow: `XrdOucPreload()` computes the versioned path with `XrdOucVerName::Version()`, writes a path-too-long message on failure, clears the error buffer, and calls `XrdSysPlugin::Preload()` on the versioned path. If `retry` is true, it also tries the original unversioned path.

State and persistence: Stateless locally. Successful `XrdSysPlugin::Preload()` persists the shared library image in process/plugin-loader state.

Dependencies and integration: Uses XRootD plugin version constants, `XrdOucVerName`, and `XrdSysPlugin`.

Risks and test signals: Error reporting depends on caller-provided buffer length. Tests should cover versioned success, retry fallback, path-too-long failure, and preservation of diagnostic text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.cc -->
