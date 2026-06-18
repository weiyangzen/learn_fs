# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdLoadLib.cc

Purpose: loads core xrootd runtime plugins from shared libraries: the filesystem implementation and the redirect plugin.

Important APIs/types/functions: `XrdXrootdloadFileSystem()` and `XrdXrootdloadRedirLib()`. The filesystem loader resolves `?XrdSfsGetFileSystem2` first and falls back to `XrdSfsGetFileSystem`; the redirect loader resolves `XrdXrootGetdRedirPI`.

Control flow: each function creates an `XrdOucPinLoader` with version information, resolves the expected factory symbol, invokes it with previous plugin instance and configuration/environment parameters, logs an error if no object is returned, and returns the plugin pointer. The filesystem loader exports `XRDOFSLIB` only when loading the first filesystem layer.

State and persistence behavior: no durable state beyond environment export and pinned shared-library handles held by `XrdOucPinLoader` machinery. Plugin instances may wrap or replace previous instances.

Dependencies: `XrdVersion`, `XrdOucEnv`, `XrdOucPinLoader`, `XrdSfsInterface`, `XrdSysError`, and `XrdXrootdRedirPI`.

Integration points: called during server configuration/startup to construct the active SFS/OFS stack and optional redirect policy plugin.

Risks: factory symbol spelling is ABI-critical; redirect symbol name `XrdXrootGetdRedirPI` must match plugins. Failure logs but returns null, so callers must abort or handle disabled functionality. Preferential v2 filesystem loading changes constructor signature and environment visibility.

Test signals: missing library, missing factory symbol, v2 and v1 filesystem factories, previous-filesystem chaining, redirect plugin load, version mismatch, and `XRDOFSLIB` export only for the first layer.
