# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCacheCM.hh

## Purpose
Defines the plugin ABI for cache context management modules loaded by the proxy/storage stack when a POSIX cache is enabled. The header is documentation-heavy and establishes the expected `extern "C"` initializer used by the `pss.ccmlib` directive.

## Important APIs, Types, And Functions
Forward declarations cover `XrdOucEnv`, `XrdPosixCache`, and `XrdSysLogger`. The central API is `XrdOucCacheCMInit_t`, a function pointer returning `bool` and accepting the cache object, optional logger, config filename, optional directive parameters, and optional environment. The comments prescribe the concrete exported symbol `XrdOucCacheCMInit(...)` and recommend `XrdVERSIONINFO(XrdOucCacheCMInit,<name>)` for plugin/version compatibility.

## Control Flow
There is no executable control flow in this header. Runtime flow is external: configuration loads a shared library, locates `XrdOucCacheCMInit`, passes the live `XrdPosixCache` and context objects, and treats `true` as initialization success.

## State And Persistence
The file defines no state. State is owned by the cache, the plugin implementation, and the process environment passed through `XrdOucEnv`; any persistence depends on the plugin and cache backend.

## Dependencies And Integration Points
This is an ABI contract between cache plugins, the POSIX cache layer, the XRootD logger, and pss configuration. The signature and symbol spelling are integration-critical because dynamic loading depends on C linkage.

## Risks And Test Signals
Risks are ABI drift, missing `extern "C"` linkage, omitted version information, and plugins assuming logger/config/env pointers are non-null. Test signals are plugin load tests with and without directive parameters, disabled cache behavior, and failure propagation when the initializer returns false.
