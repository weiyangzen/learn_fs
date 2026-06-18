# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFSctl.hh

## Purpose
Declares `XrdPfcFSctl`, the file-system-control plugin facade that binds the proxy file cache (`XrdPfc::Cache`) into the XRootD OFS FSctl extension point. It is a header-only declaration in this subset; implementation lives elsewhere, but this file defines the ABI-facing methods that accept control requests from OFS clients.

## Important APIs, Types, and Functions
- `class XrdPfcFSctl : public XrdOfsFSctl_PI`: implements the OFS FSctl plugin interface.
- `Configure(const char *CfgFN, const char *Parms, XrdOucEnv *envP, const Plugins &plugs)`: configures the plugin with the XRootD configuration file, parameters, environment, and plugin bundle.
- `FSctl(int cmd, int alen, const char *args, XrdSfsFile &file, XrdOucErrInfo &eInfo, const XrdSecEntity *client)`: file-scoped control entry point.
- `FSctl(int cmd, XrdSfsFSctl &args, XrdOucErrInfo &eInfo, const XrdSecEntity *client)`: structured FSctl entry point.
- Constructor `XrdPfcFSctl(XrdPfc::Cache &cInst, XrdSysLogger *logP)` stores the cache singleton reference and logger-derived diagnostics.

## Control Flow
The header establishes the virtual callbacks expected by `XrdOfsFSctl_PI`. Runtime flow is: XRootD loads/configures the plugin, then OFS dispatches control commands through one of the two `FSctl` overloads. The class can use `myCache` to route those commands into proxy-cache operations and `hProc`/trace/log members for handle processing and diagnostics.

## State and Persistence Behavior
The class itself owns no persistent cache state. It holds references/pointers to runtime objects: `myCache`, `hProc`, `Log`, `sysTrace`, and `m_traceID`. Persistent effects, if any, are delegated to `XrdPfc::Cache` or the file object passed to `FSctl`.

## Dependencies and Integration Points
Depends on `XrdOfs/XrdOfsFSctl_PI.hh` for the plugin ABI and `XrdSys/XrdSysError.hh` for logging. Forward declarations connect to OFS handles, security identities, SFS files, and cache internals. Integration risk is ABI-sensitive because method signatures override a plugin interface.

## Risks and Test Signals
Risks include implementation/header signature drift against `XrdOfsFSctl_PI`, null logger/trace handling, and authorization behavior in command handlers. Useful tests are plugin load/configuration tests, command dispatch tests for both overloads, and negative tests for malformed arguments or unauthorized clients.
