<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.hh

Purpose: Declares a small public utility for preloading XRootD plugins.

APIs and control flow: `XrdOucPreload(plib, eBuff, eBlen, retry)` loads the versioned plugin path and optionally retries the original path. It returns true on success and false with diagnostics on failure.

State and persistence: The function has no caller-visible object state, but successful preloads persist plugin images process-wide.

Dependencies and integration: Used by code that wants to force plugin libraries into memory before resolving their runtime objects.

Risks and test signals: The diagnostics buffer should be at least 1 KiB per the comment. Tests should validate retry behavior, too-small buffers, and compatibility with the full `XrdOucPinLoader` path-versioning contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPreload.hh -->
