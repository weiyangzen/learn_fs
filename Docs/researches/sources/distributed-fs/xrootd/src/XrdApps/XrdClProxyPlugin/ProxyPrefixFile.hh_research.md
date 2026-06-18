<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.hh

Purpose: declares `xrdcl_proxy::ProxyPrefixFile`, an `XrdCl::FilePlugIn` implementation that intercepts `Open()` to apply proxy-prefix rewriting and forwards the normal XrdCl file API to a contained `XrdCl::File`.

Important APIs/types/functions: overrides include `Open`, `Close`, `Stat`, `Read`, `PgRead`, several `Write` overloads, `PgWrite`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, `WriteV`, `Fcntl`, `Visa`, `IsOpen`, `SetProperty`, and `GetProperty`. Private helpers are `trim()`, `GetPrefixUrl()`, `GetExclDomains()`, `ConstructFinalUrl()`, and `GetFqdn()`. Members are `mIsOpen` and raw pointer `pFile`.

Control flow: the header defines a mostly transparent delegation layer; all operations except `Open()` assume `pFile` has already been allocated by a successful or attempted open.

State/persistence: owns `pFile` and deletes it in the implementation destructor. There is no durable state.

Dependencies/integration: integrates with `XrdClPlugInInterface`, `XrdClDefaultEnv`, `XrdCl::Buffer`, `ChunkList`, page IO APIs, vector IO APIs, and property propagation on `XrdCl::File`.

Risks/test signals: most methods dereference `pFile` without null checks, so calling operations before `Open()` can crash instead of returning `errInvalidOp`. `mIsOpen` is maintained separately from `pFile->IsOpen()` and is not visibly reset on close. Tests should exercise operation-before-open behavior, close/reopen expectations, all overloaded write paths, property forwarding, and ABI compatibility with the `FilePlugIn` interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClProxyPlugin/ProxyPrefixFile.hh -->
