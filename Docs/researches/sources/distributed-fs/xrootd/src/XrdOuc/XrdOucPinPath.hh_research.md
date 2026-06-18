<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.hh

Purpose: Declares `XrdOucPinPath()`, a third-party-facing helper for XRootD plugin name versioning.

APIs and control flow: The function accepts an original plugin path, output fallback flag, output buffer, and buffer length. It returns the primary path length or zero on buffer failure.

State and persistence: No owned state. The caller owns the buffer and decides whether to use the alternate original path.

Dependencies and integration: Keeps external code aligned with the same shared-library naming convention used by XRootD plugin loaders.

Risks and test signals: Callers must check a zero return and not assume the buffer is usable. Tests should compile an external-style caller and verify behavior for short buffers and normal plugin names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucPinPath.hh -->
